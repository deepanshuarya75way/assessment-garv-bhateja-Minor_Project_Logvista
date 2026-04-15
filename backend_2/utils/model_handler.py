import os
import joblib
import pandas as pd
import numpy as np
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def safe_load_model(filename):
    path1 = os.path.join(BASE_DIR, filename)
    path2 = os.path.join(BASE_DIR, "model", filename)
    target_path = path1 if os.path.exists(path1) else path2
    
    if os.path.exists(target_path):
        try:
            print(f">> Loading model: {filename}...")
            model = joblib.load(target_path)
            print(f">> [SUCCESS] {filename} loaded.")
            return model
        except Exception as e:
            print(f">> [ERROR] Failed to load {filename}: {str(e)}")
            return None
    
    print(f">> [WARNING] {filename} not found at {path1} or {path2}")
    return None

# MITRE-ATT&CK Inspired Stage Mapping
STAGE_MAPPING = {
    # Scouting / Recon
    "Recon": "Scouting (Reconnaissance)",
    "Analysis": "Scouting (Vulnerability Analysis)",
    "User Enumeration": "Scouting (User Harvesting)",
    
    # Gaining Access
    "Exploit": "Gaining Access (Exploitation)",
    "Fuzzer": "Gaining Access (Automated Fuzzing)",
    "Generic": "Gaining Access (Brute Force)",
    "Brute Force Attempt": "Gaining Access (Auth Attack)",
    
    # Persistence
    "Backdoor": "Persistence (Persistence)",
    "Malware": "Persistence (Malicious Payload)",
    "Worms": "Persistence (Self-Propagating)",
    
    # Privilege Escalation
    "Privilege Escalation": "Privileged Access (Unauthorized Escalation)",
    "Role escalation": "Privileged Access (Administrative Change)",
    "Privilege Change": "Privileged Access (User Modification)",
    
    # Impact / Exfiltration
    "DoS": "Service Disruption (Denial of Service)",
    "Data Infiltration": "Data Theft (Exfiltration)",
    "Insider Attack": "Data Theft (Internal Leakage)",
    "Data download": "Data Theft (Unauthorized Download)",
    "File Download": "Data Theft (Exfiltration)",
    
    # Normal / Benign
    "Normal": "Normal Activity",
    "Authentication Success": "Account Access (Successful Login)",
    "Critical Privilege Access": "System Hijack (Privileged Initial Access)",
    "System Activity": "Normal (Routine Process)",
    "General Event": "System Activity"
}

class ModelManager:
    def __init__(self):
        # UNSW network model setup
        self.unsw_model = safe_load_model('unsw_model.pkl')
        self.unsw_encoders = safe_load_model('encoders.pkl')
        self.unsw_target = safe_load_model('target_encoder.pkl')
        self.unsw_iso = safe_load_model('iso_model.pkl')
        
        # EVTX windows model setup
        self.evtx_model = safe_load_model('evtx_model.pkl')
        self.evtx_encoders = safe_load_model('feature_encoders.pkl')
        self.evtx_target = safe_load_model('evtx_target_encoder.pkl') or safe_load_model('target_encoder.pkl')
        
    def extract_features(self, log_dict):
        if isinstance(log_dict, dict):
            return log_dict
        if isinstance(log_dict, str):
            try:
                data = json.loads(log_dict)
                if isinstance(data, dict):
                    return data
            except:
                pass
        return {"raw_log": str(log_dict)}
    
    def _predict_unsw(self, feature_dict):
        if not self.unsw_model:
            return "Uncertain"
            
        df = pd.DataFrame([feature_dict])
        
        if self.unsw_encoders:
            for col, encoder in self.unsw_encoders.items():
                if col in df.columns:
                    try:
                        val = df[col].iloc[0]
                        if val in encoder.classes_:
                            df[col] = encoder.transform([val])[0]
                        else:
                            df[col] = encoder.transform([encoder.classes_[0]])[0]
                    except:
                        df[col] = 0
        
        if hasattr(self.unsw_model, "feature_names_in_"):
            expected_features = list(self.unsw_model.feature_names_in_)
            for f in expected_features:
                if f not in df.columns:
                    df[f] = 0
            df = df[expected_features]
        else:
            df = df.select_dtypes(exclude=['object'])
            if df.empty:
               return "Uncertain"
               
        df.fillna(0, inplace=True)
        
        anomaly = False
        if self.unsw_iso:
            try:
                iso_df = df.copy()
                if hasattr(self.unsw_iso, "feature_names_in_"):
                    iso_feats = list(self.unsw_iso.feature_names_in_)
                    for f in iso_feats:
                        if f not in iso_df.columns:
                            iso_df[f] = 0
                    iso_df = iso_df[iso_feats]
                
                iso_pred = self.unsw_iso.predict(iso_df)[0]
                if iso_pred == -1:
                    anomaly = True
            except:
                pass
                
        if anomaly:
            return "Unknown Attack"
            
        try:
            pred = self.unsw_model.predict(df)[0]
            if self.unsw_target:
                pred = self.unsw_target.inverse_transform([pred])[0]
            return str(pred)
        except Exception:
            return "Uncertain"
            
    def _predict_evtx(self, feature_dict):
        if not self.evtx_model:
             return "Uncertain"
             
        df = pd.DataFrame([feature_dict])
        
        if self.evtx_encoders:
            for col, encoder in self.evtx_encoders.items():
                if col in df.columns:
                    try:
                        val = df[col].iloc[0]
                        if val in encoder.classes_:
                            df[col] = encoder.transform([val])[0]
                        else:
                            df[col] = 0
                    except:
                        df[col] = 0

        if hasattr(self.evtx_model, "feature_names_in_"):
            expected_features = list(self.evtx_model.feature_names_in_)
            for f in expected_features:
                if f not in df.columns:
                    df[f] = 0
            df = df[expected_features]
        else:
            df = df.select_dtypes(exclude=['object'])
            if df.empty:
                 return "Uncertain"
                 
        df.fillna(0, inplace=True)
        
        try:
            pred = self.evtx_model.predict(df)[0]
            if self.evtx_target:
                pred = self.evtx_target.inverse_transform([pred])[0]
            return str(pred)
        except:
            return "Uncertain"

    def _predict_auth(self, log_str):
        log_lower = str(log_str).lower()
        # High-Priority Success Detection
        if any(kw in log_lower for kw in ["accepted", "session opened", "login_success"]):
            if "root" in log_lower or "admin" in log_lower:
                return "Critical Privilege Access"
            return "Authentication Success"
            
        # Attack Detection
        if any(kw in log_lower for kw in ["failed password", "authentication failure", "failed to login"]):
            return "Brute Force Attempt"
        if "invalid user" in log_lower:
            return "User Enumeration"
        return "System Activity"

    def predict(self, log_dict, log_type):
        features = self.extract_features(log_dict)
        raw_log = features.get("raw_log", str(log_dict))
        raw_lower = raw_log.lower()
        
        # Keyword-based Overrides (Forensic Heuristics)
        if any(kw in raw_lower for kw in ["/etc/shadow", "backup.sql", ".dump", "aws_secret"]):
            return "File Download"
        if any(kw in raw_lower for kw in ["select", "union", "insert", "drop"]) and log_type == "web":
            return "Exploit"
        
        if log_type in ["web", "firewall"]:
            res = self._predict_unsw(features)
            return res if res != "Normal" else "Normal"
        elif log_type == "windows":
            return self._predict_evtx(features)
        elif log_type in ["linux_auth", "auth_event", "linux_system"]:
            return self._predict_auth(raw_log)
        else:
            return "General Event"

MODEL_MANAGER = None

def evaluate_log(log_str, log_type):
    global MODEL_MANAGER
    if MODEL_MANAGER is None:
        print(">> Bootstrapping AI Models (this can take up to 20 seconds, please wait...)")
        MODEL_MANAGER = ModelManager()
        print(">> ML Models successfully loaded into Pipeline.")
    return MODEL_MANAGER.predict(log_str, log_type)
