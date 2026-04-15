import os
import joblib
from log_parser import parse_log, prepare_features, FEATURE_COLUMNS

def print_result(is_anomaly, attack_class):
    """Formats and prints the result like the requirements specified."""
    if is_anomaly:
        if attack_class == "Normal":
            print("Anomaly Detected (Unknown Pattern)")
        else:
            print(f"Anomaly + Classified as {attack_class}")
    else:
        # If it's not an anomaly by the Isolation Forest
        if attack_class == "Normal":
            print("Normal")
        else:
            print(f"{attack_class}")

def main():
    print("Initializing AI Log Investigation Framework...")
    
    # 1. Load Models and Encoders
    try:
        rf_model = joblib.load('model/unsw_model.pkl')
        iso_model = joblib.load('model/iso_model.pkl')
        encoders = joblib.load('model/encoders.pkl')
        target_encoder = joblib.load('model/target_encoder.pkl')
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Please run `python train.py` first to generate models.")
        return

    # 2. Sample raw log
    # A single line representing a piece of network log (first 47 columns without label/attack_cat)
    # This one resembles a typical "Normal" log for demonstration
    sample_log = "59.166.0.0,1390,149.171.126.6,53,udp,CON,0.001055,132,164,31,29,0,0,dns,500473.9375,621800.9375,2,2,0,0,0,0,66,82,0,0,0,0,1421927414,1421927414,0.017,0.013,0,0,0,0,0,0,0,0,3,2,1,1,1,1,1"
    
    # Another sample log for testing (simulating a DoS or similar high-load/anomaly profile)
    sample_malware_log = "175.45.176.0,47439,149.171.126.18,53,udp,INT,0.000009,114,0,254,0,0,0,dns,50666664,0,2,0,0,0,0,0,57,0,0,0,0,0,1421927414,1421927414,0.009,0,0,0,0,0,2,0,0,0,1,1,1,1,1,1,1"
    
    logs_to_test = [
         ("Log 1 (Expected Normal)", sample_log),
         ("Log 2 (Expected Attack)", sample_malware_log)
    ]
    
    for log_name, log_str in logs_to_test:
        print(f"\n--- Processing {log_name} ---")
        # 3. Parse Log
        parsed_dict = parse_log(log_str)
        
        # 4. Convert to Features
        feature_df = prepare_features(parsed_dict, encoders, FEATURE_COLUMNS)
        
        # 5. Run Models
        # a) Isolation Forest (1 = Normal/Inlier, -1 = Anomaly/Outlier)
        anomaly_pred = iso_model.predict(feature_df)[0]
        is_anomaly = (anomaly_pred == -1)
        
        # b) Random Forest
        attack_pred = rf_model.predict(feature_df)[0]
        
        # Decode the target index to human readable attack class
        attack_class = target_encoder.inverse_transform([attack_pred])[0]
        
        # 6. Output Result
        print_result(is_anomaly, attack_class)

if __name__ == "__main__":
    main()
