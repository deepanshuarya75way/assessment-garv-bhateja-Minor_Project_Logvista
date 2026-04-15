import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DATA_FILE = 'eventlog.csv'
TARGET_COLUMN = 'EVTX_Tactic'
MODEL_FILE = 'evtx_model.pkl'
FEATURE_ENCODERS_FILE = 'feature_encoders.pkl'
TARGET_ENCODER_FILE = 'target_encoder.pkl'

# Allowed features based on requirements
ALLOWED_FEATURES = [
    'EventID',
    'Channel',
    'Computer',
    'AuthenticationPackageName',
    'IpAddress',
    'EventRecordID',
    'ProcessName',
    'CommandLine',
    'TargetUserName',
    'SourceUserName',
    # Adding eventlog.csv structure columns so it doesn't crash from 0 features
    'MachineName', 'Category', 'EntryType', 'Message', 'Source', 
    'TimeGenerated', 'country', 'regionName', 'city', 'timezone', 'isp'
]

class SafeLabelEncoder:
    """
    A custom LabelEncoder that handles unseen values during transform.
    Unseen values are mapped to a special 'UNKNOWN' category.
    """
    def __init__(self):
        self.classes_ = np.array([])
        self.class_to_idx = {}
        self.unknown_idx = -1

    def fit(self, y):
        # We add 'UNKNOWN' to handle unseen inference values if it's not present
        unique_classes = pd.Series(y).astype(str).unique()
        if 'UNKNOWN' not in unique_classes:
            unique_classes = np.append(unique_classes, 'UNKNOWN')
        
        self.classes_ = unique_classes
        self.class_to_idx = {val: idx for idx, val in enumerate(self.classes_)}
        self.unknown_idx = self.class_to_idx['UNKNOWN']
        return self

    def transform(self, y):
        return np.array([self.class_to_idx.get(str(val), self.unknown_idx) for val in y])

    def fit_transform(self, y):
        return self.fit(y).transform(y)

def load_and_preprocess_data(filepath):
    logging.info(f"Loading dataset from {filepath}...")
    try:
        df = pd.read_csv(filepath, low_memory=False)
    except FileNotFoundError:
        logging.error(f"File {filepath} not found. Please ensure the dataset exists.")
        return None, None
        
    if TARGET_COLUMN not in df.columns:
        logging.warning(f"Target column '{TARGET_COLUMN}' not found. Creating a dummy target column for testing pipeline.")
        dummy_classes = [
            'Credential Access', 'Defense Evasion', 'Privilege Escalation', 'Persistence',
            'Lateral Movement', 'Execution', 'Command and Control', 'Discovery', 'Normal'
        ]
        df[TARGET_COLUMN] = np.random.choice(dummy_classes, size=len(df))

    # Filter columns that exist
    existing_features = [col for col in ALLOWED_FEATURES if col in df.columns]
    logging.info(f"Found {len(existing_features)} relevant features out of {len(ALLOWED_FEATURES)}")
    
    # Keep only existing features + target
    columns_to_keep = existing_features + [TARGET_COLUMN]
    df = df[columns_to_keep]

    # Handle missing values
    for col in existing_features:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(-1)
        else:
            df[col] = df[col].fillna("UNKNOWN")
            
    df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna("UNKNOWN")

    return df, existing_features

def train_model():
    df, features = load_and_preprocess_data(DATA_FILE)
    if df is None:
        return

    features_to_encode = []
    numeric_features = []
    
    for col in features:
        if not pd.api.types.is_numeric_dtype(df[col]):
            features_to_encode.append(col)
        else:
            numeric_features.append(col)

    logging.info("Encoding features...")
    feature_encoders = {}
    
    for col in features_to_encode:
        encoder = SafeLabelEncoder()
        df[col] = encoder.fit_transform(df[col])
        feature_encoders[col] = encoder
        
    logging.info("Encoding target...")
    target_encoder = LabelEncoder()
    # For target we only expect known classes but good to encode as standard
    y = target_encoder.fit_transform(df[TARGET_COLUMN])
    
    X = df[features]

    logging.info("Splitting dataset 80/20 with stratification...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    logging.info("Training RandomForestClassifier...")
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42
    )
    
    clf.fit(X_train, y_train)

    logging.info("Evaluating model...")
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    logging.info(f"Accuracy: {acc:.4f}")
    
    report = classification_report(y_test, y_pred, target_names=target_encoder.classes_)
    logging.info(f"Classification Report:\n{report}")

    logging.info("Saving models and encoders...")
    joblib.dump(clf, MODEL_FILE)
    joblib.dump({
        'encoders': feature_encoders,
        'features': features,
        'numeric': numeric_features,
        'categorical': features_to_encode
    }, FEATURE_ENCODERS_FILE)
    joblib.dump(target_encoder, TARGET_ENCODER_FILE)
    
    logging.info("Training pipeline completed successfully.")

def predict_evtx_log(log_dict):
    """
    Predicts the attack tactic for a single log dictionary.
    
    Args:
        log_dict (dict): A dictionary representing a single EVTX log.
        
    Returns:
        str: The predicted MITRE ATT&CK category.
    """
    # Load model and encoders if they exist
    try:
        model = joblib.load(MODEL_FILE)
        feature_data = joblib.load(FEATURE_ENCODERS_FILE)
        target_encoder = joblib.load(TARGET_ENCODER_FILE)
    except FileNotFoundError:
        return "ERROR: Model or encoders not found. Please train the model first."

    feature_encoders = feature_data['encoders']
    features = feature_data['features']
    numeric_features = feature_data['numeric']
    categorical_features = feature_data['categorical']

    # Prepare input data based on trained features
    # If a feature was in training but missing from log_dict, we fill it appropriately
    processed_log = {}
    
    for feature in features:
        val = log_dict.get(feature)
        
        if feature in numeric_features:
            if val is None or pd.isna(val):
                processed_log[feature] = -1
            else:
                try:
                    processed_log[feature] = float(val)
                except ValueError:
                    processed_log[feature] = -1
        else: # Categorical
            if val is None or pd.isna(val) or str(val).strip() == "":
                val = "UNKNOWN"
            else:
                val = str(val)
            
            # Encode using SafeLabelEncoder
            encoder = feature_encoders[feature]
            idx = encoder.transform([val])[0]
            processed_log[feature] = idx
            
    # Create DataFrame for prediction (model expects 2D array / DataFrame with correct columns)
    df_pred = pd.DataFrame([processed_log])[features]
    
    # Predict
    pred_idx = model.predict(df_pred)[0]
    
    # Decode target
    try:
        predicted_label = target_encoder.inverse_transform([pred_idx])[0]
    except Exception:
        predicted_label = "UNKNOWN_TARGET"
        
    return predicted_label

if __name__ == "__main__":
    train_model()
    
    # ---------------------------------------------------------
    # Example inference test (uncomment to test):
    # ---------------------------------------------------------
    # test_log = {
    #     "EventID": 4624,
    #     "Channel": "Security",
    #     "Computer": "DC01.corp.local",
    #     "ProcessName": "C:\\Windows\\System32\\svchost.exe",
    #     "NonExistentCol": "Should be ignored"
    # }
    # print("Inference Output:", predict_evtx_log(test_log))
