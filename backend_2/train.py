import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib

# Define the exact columns as per requirements
COLUMNS = [
    "srcip", "sport", "dstip", "dsport", "proto", "state", "dur", "sbytes", "dbytes", "sttl", "dttl",
    "sloss", "dloss", "service", "Sload", "Dload", "Spkts", "Dpkts", "swin", "dwin", "stcpb", "dtcpb",
    "smeansz", "dmeansz", "trans_depth", "res_bdy_len", "Sjit", "Djit", "Stime", "Ltime", "Sintpkt",
    "Dintpkt", "tcprtt", "synack", "ackdat", "is_sm_ips_ports", "ct_state_ttl", "ct_flw_http_mthd",
    "is_ftp_login", "ct_ftp_cmd", "ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm", "attack_cat", "label"
]

def map_attack_category(attack_cat):
    """Maps the original attack categories to more granular types."""
    if pd.isna(attack_cat):
        return "Normal"
    
    attack_cat = str(attack_cat).strip().lower()
    
    if attack_cat == "dos":
        return "DoS"
    elif attack_cat == "exploits":
        return "Exploit"
    elif attack_cat == "fuzzers":
        return "Fuzzer"
    elif attack_cat == "reconnaissance":
        return "Recon"
    elif attack_cat == "analysis":
        return "Analysis"
    elif attack_cat == "backdoors":
        return "Backdoor"
    elif attack_cat == "generic":
        return "Generic"
    elif attack_cat in ["shellcode", "worms"]:
        return "Malware"
    elif attack_cat == "normal":
        return "Normal"
    else:
        # Fallback for any other types
        return "Other Attack"


def main():
    print("Starting Training Pipeline...")
    
    # 1. DATA LOADING (CHUNKED FOR MEMORY EFFICIENCY)
    print("Loading Dataset in chunks...")
    csv_path = "UNSW-NB15_1.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Please make sure it exists in the current directory.")
        return
        
    # We will read chunks, map them immediately, and collect all attacks + some normals
    chunk_list = []
    normal_samples = []
    
    try:
        reader = pd.read_csv(csv_path, header=None, names=COLUMNS, chunksize=100000, low_memory=False)
        for i, chunk in enumerate(reader):
            print(f"Processing chunk {i+1}...")
            # Basic Cleaning per chunk
            chunk['attack_cat'] = chunk['attack_cat'].fillna("Normal")
            chunk['attack_type'] = chunk['attack_cat'].apply(map_attack_category)
            
            # Separate attacks and normal
            attacks = chunk[chunk['attack_type'] != 'Normal']
            normals = chunk[chunk['attack_type'] == 'Normal']
            
            chunk_list.append(attacks)
            # Sample normals from each chunk to keep memory low (e.g. 5000 per chunk)
            if not normals.empty:
                normal_samples.append(normals.sample(n=min(len(normals), 10000), random_state=42))
    except Exception as e:
        print(f"Error during chunked reading: {e}")
        return

    # Combine collected rows
    print("Combining sampled data...")
    df = pd.concat(chunk_list + normal_samples)
    print(f"Final training set size: {len(df)} rows")
    print(df['attack_type'].value_counts())

    # Ensure categorical and numerical columns are handled
    categorical_cols = ['srcip', 'sport', 'dstip', 'dsport', 'proto', 'state', 'service']
    for col in categorical_cols:
        df[col] = df[col].astype(str).fillna("Unknown")
        
    numerical_cols = [c for c in COLUMNS if c not in categorical_cols + ['attack_cat', 'label']]
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(np.float32)

    # 4. FEATURE PROCESSING
    print("Processing Features...")
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        
    # 5. TARGET ENCODING
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(df['attack_type'])
    X = df.drop(columns=['attack_cat', 'label', 'attack_type']).astype(np.float32)
    
    # Normal data for Isolation Forest
    X_normal_only = X[df['attack_type'] == 'Normal'].copy()

    # 6. TRAIN/TEST SPLIT
    print("Splitting Data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # 7. HANDLE CLASS IMBALANCE
    print("Handling Class Imbalance with SMOTE...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    # 8. MODEL TRAINING (Random Forest)
    print(f"Training Random Forest Classifier (n_estimators=200)...")
    rf_model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_resampled, y_train_resampled)
    
    # 9. EVALUATION
    print("Evaluating Model...")
    y_pred = rf_model.predict(X_test)
    classes_names = target_encoder.classes_
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=classes_names))
    
    # 11. BUILD ANOMALY MODEL (Isolation Forest)
    print("Training Isolation Forest on Normal Data...")
    iso_model = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
    iso_model.fit(X_normal_only)
    
    # 10. SAVE ARTIFACTS
    print("Saving Models and Encoders...")
    os.makedirs('model', exist_ok=True)
    joblib.dump(rf_model, 'model/unsw_model.pkl')
    joblib.dump(encoders, 'model/encoders.pkl')
    joblib.dump(target_encoder, 'model/target_encoder.pkl')
    joblib.dump(iso_model, 'model/iso_model.pkl')
    
    print("Training Pipeline Complete. Artifacts saved in 'model/' directory.")


if __name__ == "__main__":
    main()
