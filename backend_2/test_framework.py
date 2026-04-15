import pandas as pd
import joblib
import os
from log_parser import parse_log, prepare_features, FEATURE_COLUMNS

# Configuration
CSV_PATH = "UNSW-NB15_1.csv"
MODEL_DIR = "model"

def load_ai_system():
    """Loads all models and encoders."""
    print("Loading AI Forensic Models...")
    rf_model = joblib.load(os.path.join(MODEL_DIR, 'unsw_model.pkl'))
    iso_model = joblib.load(os.path.join(MODEL_DIR, 'iso_model.pkl'))
    encoders = joblib.load(os.path.join(MODEL_DIR, 'encoders.pkl'))
    target_encoder = joblib.load(os.path.join(MODEL_DIR, 'target_encoder.pkl'))
    return rf_model, iso_model, encoders, target_encoder

def test_on_real_samples(n=5):
    """Picks random samples from the dataset and runs the pipeline."""
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    # Load models
    rf, iso, encoders, target_le = load_ai_system()

    print(f"\n--- Testing on {n} random samples from the dataset ---\n")

    # Read a random sample of lines
    # We use skiprows to pick a random starting point in the large file
    file_size = os.path.getsize(CSV_PATH)
    df_sample = pd.read_csv(CSV_PATH, header=None, nrows=n, skiprows=100000) # Testing mid-dataset

    for i, row in df_sample.iterrows():
        # 1. Prepare raw log string (first 47 columns)
        raw_log_list = [str(val) for val in row.values[:47]]
        raw_log_str = ",".join(raw_log_list)
        
        # 2. Extract Ground Truth (for verification only)
        actual_cat = str(row.values[47]).strip()
        actual_label = "Attack" if row.values[48] == 1 else "Normal"

        # 3. RUN THE PIPELINE
        parsed = parse_log(raw_log_str)
        features = prepare_features(parsed, encoders, FEATURE_COLUMNS)
        
        # Is it an Anomaly?
        is_anomaly = iso.predict(features)[0] == -1
        
        # What is the Classification?
        pred_idx = rf.predict(features)[0]
        pred_class = target_le.inverse_transform([pred_idx])[0]

        # 4. Output Results
        print(f"Sample #{i+1}:")
        print(f"  [Actual Data]  Category: {actual_cat} ({actual_label})")
        
        status = "Normal"
        if is_anomaly:
            status = f"Anomaly + Classified as {pred_class}"
        else:
            status = pred_class
            
        print(f"  [AI PREDICTION] Result: {status}")
        
        # Simple Validation Check
        if pred_class.lower() == "normal" and actual_label == "Normal":
            print("  ✅ Match: Correctly identified as Normal.")
        elif pred_class.lower() != "normal" and actual_label == "Attack":
            print(f"  🔥 Match: Correctly identified {pred_class} attack!")
        else:
            print("  ❌ Mismatch: Check model confidence.")
        print("-" * 50)

if __name__ == "__main__":
    test_on_real_samples(5)
