import pandas as pd
import numpy as np

# Model feature columns (excluding attack_cat, attack_type and label)
FEATURE_COLUMNS = [
    "srcip", "sport", "dstip", "dsport", "proto", "state", "dur", "sbytes", "dbytes", "sttl", "dttl",
    "sloss", "dloss", "service", "Sload", "Dload", "Spkts", "Dpkts", "swin", "dwin", "stcpb", "dtcpb",
    "smeansz", "dmeansz", "trans_depth", "res_bdy_len", "Sjit", "Djit", "Stime", "Ltime", "Sintpkt",
    "Dintpkt", "tcprtt", "synack", "ackdat", "is_sm_ips_ports", "ct_state_ttl", "ct_flw_http_mthd",
    "is_ftp_login", "ct_ftp_cmd", "ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm"
]

def parse_log(log: str) -> dict:
    """
    Takes a comma-separated log string and returns a dictionary mapped to feature keys.
    We assume the log string contains 47 feature columns (no attack_cat, no label).
    If it contains 49, it will discard the last two.
    """
    fields = log.strip().split(',')
    
    parsed_dict = {}
    for i, col in enumerate(FEATURE_COLUMNS):
        if i < len(fields):
            parsed_dict[col] = fields[i].strip()
        else:
            parsed_dict[col] = None # Field missing in log length
            
    return parsed_dict

def prepare_features(parsed_log: dict, encoders: dict, feature_columns: list) -> pd.DataFrame:
    """
    Converts a parsed log dictionary into a model-ready data structure (pandas DataFrame).
    Applies encoding and fills missing columns appropriately.
    """
    # Create DataFrame with 1 row
    df = pd.DataFrame([parsed_log])
    
    # Identify categorical vs numerical based on encoder keys
    categorical_cols = list(encoders.keys())
    numerical_cols = [c for c in feature_columns if c not in categorical_cols]
    
    # Clean Categoricals
    for col in categorical_cols:
        if col in df.columns:
            # Handle unknown values that encoder hasn't seen
            val = str(df[col].iloc[0])
            if val == 'None' or val == '':
                val = "Unknown"
            
            # Use 'Unknown' class fallback if not in classes_
            # Since 'Unknown' was trained, it should be in classes_
            if val not in encoders[col].classes_:
                val = "Unknown" 
                # If still not there due to some edge case, fallback to first class
                if val not in encoders[col].classes_:
                    val = encoders[col].classes_[0]
            
            df[col] = encoders[col].transform([val])[0]
        else:
            # Column entirely missing
            df[col] = encoders[col].transform(["Unknown"])[0] if "Unknown" in encoders[col].classes_ else encoders[col].classes_[0]

    # Clean Numericals
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0.0

    # Ensure right exact column order
    df = df[feature_columns]
    
    return df
