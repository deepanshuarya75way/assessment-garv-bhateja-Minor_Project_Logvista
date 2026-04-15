import joblib
import pandas as pd
import numpy as np
import os
from log_parser import prepare_features, FEATURE_COLUMNS
from datetime import datetime, timedelta

# 1. Your provided JSON logs
json_logs = [
    {"timestamp":"2026-04-03T09:00:01Z","source":"web_server","event_type":"http_request","ip":"192.168.1.2","status":"normal","severity":"low","message":"GET /home"},
    {"timestamp":"2026-04-03T09:01:15Z","source":"auth_server","event_type":"login_success","user":"user1","ip":"192.168.1.3","status":"normal","severity":"low","message":"Login successful"},
    {"timestamp":"2026-04-03T09:02:22Z","source":"web_server","event_type":"http_request","ip":"192.168.1.4","status":"normal","severity":"low","message":"GET /products"},
    {"timestamp":"2026-04-03T09:03:10Z","source":"database_server","event_type":"query","ip":"192.168.1.5","status":"normal","severity":"low","message":"SELECT * FROM products"},
    {"timestamp":"2026-04-03T09:04:45Z","source":"auth_server","event_type":"login_failed","user":"admin","ip":"203.0.113.1","status":"suspicious","severity":"medium","message":"Failed login"},
    {"timestamp":"2026-04-03T09:05:10Z","source":"auth_server","event_type":"login_failed","user":"admin","ip":"203.0.113.1","status":"suspicious","severity":"medium","message":"Failed login"},
    {"timestamp":"2026-04-03T09:05:30Z","source":"auth_server","event_type":"login_failed","user":"admin","ip":"203.0.113.1","status":"malicious","severity":"high","threat_type":"Brute Force","message":"Multiple failed logins"},
    {"timestamp":"2026-04-03T09:06:00Z","source":"web_server","event_type":"http_request","ip":"198.51.100.10","status":"malicious","severity":"critical","threat_type":"SQL Injection","message":"' OR '1'='1"},
    {"timestamp":"2026-04-03T09:07:12Z","source":"network_monitor","event_type":"traffic_spike","ip":"45.1.1.1","status":"malicious","severity":"critical","threat_type":"DDoS","message":"Distributed traffic spike"},
    {"timestamp":"2026-04-03T09:08:20Z","source":"web_server","event_type":"request_flood","ip":"203.0.113.55","status":"malicious","severity":"critical","threat_type":"DoS","message":"Single IP flood"},
    {"timestamp":"2026-04-03T09:09:30Z","source":"endpoint_security","event_type":"file_execution","user":"user2","ip":"192.168.1.6","status":"malicious","severity":"high","threat_type":"Malware Attack","message":"Unknown executable"},
    {"timestamp":"2026-04-03T09:10:10Z","source":"database_server","event_type":"data_access","user":"emp1","ip":"192.168.1.7","status":"suspicious","severity":"medium","threat_type":"Data Infiltration","message":"Large data access"},
    {"timestamp":"2026-04-03T09:11:15Z","source":"internal_system","event_type":"privilege_change","user":"emp2","ip":"192.168.1.8","status":"malicious","severity":"high","threat_type":"Privilege Escalation","message":"Unauthorized privilege change"},
    {"timestamp":"2026-04-03T09:12:05Z","source":"internal_system","event_type":"data_download","user":"emp3","ip":"192.168.1.9","status":"malicious","severity":"high","threat_type":"Insider Attack","message":"Sensitive download"},
    {"timestamp":"2026-04-03T09:13:40Z","source":"web_server","event_type":"http_request","ip":"192.168.1.10","status":"normal","severity":"low","message":"GET /contact"},
    {"timestamp":"2026-04-03T09:14:22Z","source":"auth_server","event_type":"login_success","user":"user3","ip":"192.168.1.11","status":"normal","severity":"low","message":"Login success"},
    {"timestamp":"2026-04-03T09:15:01Z","source":"web_server","event_type":"http_request","ip":"192.168.1.12","status":"normal","severity":"low","message":"GET /about"},
    {"timestamp":"2026-04-03T09:16:30Z","source":"database_server","event_type":"query","ip":"192.168.1.13","status":"normal","severity":"low","message":"SELECT orders"},
    {"timestamp":"2026-04-03T09:17:42Z","source":"web_server","event_type":"http_request","ip":"198.51.100.20","status":"malicious","severity":"critical","threat_type":"SQL Injection","message":"UNION SELECT"},
    {"timestamp":"2026-04-03T09:18:55Z","source":"network_monitor","event_type":"traffic_spike","ip":"45.2.2.2","status":"malicious","severity":"critical","threat_type":"DDoS","message":"Botnet traffic"},
    {"timestamp":"2026-04-03T09:19:10Z","source":"web_server","event_type":"request_flood","ip":"203.0.113.60","status":"malicious","severity":"critical","threat_type":"DoS","message":"High requests"},
    {"timestamp":"2026-04-03T09:20:30Z","source":"endpoint_security","event_type":"file_execution","user":"user4","ip":"192.168.1.14","status":"malicious","severity":"high","threat_type":"Malware Attack","message":"Suspicious exe"},
    {"timestamp":"2026-04-03T09:21:40Z","source":"database_server","event_type":"data_access","user":"emp4","ip":"192.168.1.15","status":"suspicious","severity":"medium","threat_type":"Data Infiltration","message":"Bulk read"},
    {"timestamp":"2026-04-03T09:22:10Z","source":"internal_system","event_type":"privilege_change","user":"emp5","ip":"192.168.1.16","status":"malicious","severity":"high","threat_type":"Privilege Escalation","message":"Role escalation"},
    {"timestamp":"2026-04-03T09:23:33Z","source":"internal_system","event_type":"data_download","user":"emp6","ip":"192.168.1.17","status":"malicious","severity":"high","threat_type":"Insider Attack","message":"Confidential export"},
    {"timestamp":"2026-04-03T09:24:10Z","source":"web_server","event_type":"http_request","ip":"192.168.1.18","status":"normal","severity":"low","message":"GET /login"},
    {"timestamp":"2026-04-03T09:25:12Z","source":"auth_server","event_type":"login_success","user":"user5","ip":"192.168.1.19","status":"normal","severity":"low","message":"Login success"},
    {"timestamp":"2026-04-03T09:26:15Z","source":"web_server","event_type":"http_request","ip":"192.168.1.20","status":"normal","severity":"low","message":"GET /dashboard"},
    {"timestamp":"2026-04-03T09:27:20Z","source":"database_server","event_type":"query","ip":"192.168.1.21","status":"normal","severity":"low","message":"SELECT users"},
    {"timestamp":"2026-04-03T09:28:10Z","source":"auth_server","event_type":"login_failed","user":"root","ip":"203.0.113.70","status":"suspicious","severity":"medium","message":"Failed login"},
    {"timestamp":"2026-04-03T09:28:30Z","source":"auth_server","event_type":"login_failed","user":"root","ip":"203.0.113.70","status":"malicious","severity":"high","threat_type":"Brute Force","message":"Repeated attempts"},
    {"timestamp":"2026-04-03T09:29:50Z","source":"web_server","event_type":"http_request","ip":"198.51.100.30","status":"malicious","severity":"critical","threat_type":"SQL Injection","message":"DROP TABLE users"},
    {"timestamp":"2026-04-03T09:30:30Z","source":"network_monitor","event_type":"traffic_spike","ip":"45.3.3.3","status":"malicious","severity":"critical","threat_type":"DDoS","message":"Massive traffic"},
    {"timestamp":"2026-04-03T09:31:00Z","source":"web_server","event_type":"request_flood","ip":"203.0.113.80","status":"malicious","severity":"critical","threat_type":"DoS","message":"Flood detected"},
    {"timestamp":"2026-04-03T09:32:10Z","source":"endpoint_security","event_type":"file_execution","user":"user6","ip":"192.168.1.22","status":"malicious","severity":"high","threat_type":"Malware Attack","message":"Trojan execution"},
    {"timestamp":"2026-04-03T09:33:40Z","source":"database_server","event_type":"data_access","user":"emp7","ip":"192.168.1.23","status":"suspicious","severity":"medium","threat_type":"Data Infiltration","message":"Data extraction"},
    {"timestamp":"2026-04-03T09:34:20Z","source":"internal_system","event_type":"privilege_change","user":"emp8","ip":"192.168.1.24","status":"malicious","severity":"high","threat_type":"Privilege Escalation","message":"Admin rights granted"},
    {"timestamp":"2026-04-03T09:35:05Z","source":"internal_system","event_type":"data_download","user":"emp9","ip":"192.168.1.25","status":"malicious","severity":"high","threat_type":"Insider Attack","message":"Sensitive export"},
    {"timestamp":"2026-04-03T09:36:10Z","source":"web_server","event_type":"http_request","ip":"192.168.1.26","status":"normal","severity":"low","message":"GET /faq"},
    {"timestamp":"2026-04-03T09:37:22Z","source":"auth_server","event_type":"login_success","user":"user7","ip":"192.168.1.27","status":"normal","severity":"low","message":"Login success"},
    {"timestamp":"2026-04-03T09:38:30Z","source":"web_server","event_type":"http_request","ip":"192.168.1.28","status":"normal","severity":"low","message":"GET /profile"},
    {"timestamp":"2026-04-03T09:39:10Z","source":"database_server","event_type":"query","ip":"192.168.1.29","status":"normal","severity":"low","message":"SELECT logs"},
    {"timestamp":"2026-04-03T09:40:05Z","source":"web_server","event_type":"http_request","ip":"192.168.1.30","status":"normal","severity":"low","message":"GET /logout"}
]

# Attack Stage Mapping for Investigation Timeline
STAGE_MAPPING = {
    "Recon": "Scouting (Reconnaissance)",
    "Analysis": "Scouting (Vulnerability Analysis)",
    "Exploit": "Gaining Access (Exploitation)",
    "Fuzzer": "Gaining Access (Automated Fuzzing)",
    "Generic": "Gaining Access (Brute Force)",
    "Backdoor": "Persistence (Backdoor Installed)",
    "Malware": "Persistence (Malicious Payload)",
    "DoS": "Disruption (Denial of Service)",
    "Worms": "Disruption (Self-Propagating Malware)",
    "Normal": "Normal Activity"
}

SIMULATED_MAPPING = {
    "Data Infiltration": "Exfiltration (Unauthorized Data Theft)",
    "Insider Attack": "Exfiltration (Confidential Data Export)",
    "Privilege Escalation": "Privilege Escalation (Unauthorized Elevation)"
}

def simulate_network_features(log):
    """
    Bridges high-level JSON logs to low-level Network Features.
    """
    features = {col: 0 for col in FEATURE_COLUMNS}
    features['srcip'] = log.get('ip', '0.0.0.0')
    features['proto'] = 'tcp'
    features['state'] = 'CON'
    features['dur'] = 0.5
    features['sttl'] = 31 
    features['dttl'] = 29
    
    status = log.get('status', 'normal')
    threat = log.get('threat_type', '')

    if status in ['suspicious', 'malicious']:
        features['sttl'] = 254
        features['state'] = 'INT'
        features['ct_state_ttl'] = 6

    if threat == "DoS":
        features['Sload'] = 20000000
        features['Spkts'] = 10000
        features['proto'] = 'udp'
        features['dur'] = 0.00001
        features['dbytes'] = 0
    elif threat == "SQL Injection":
        features['service'] = 'http'
        features['sbytes'] = 60000
        features['trans_depth'] = 5
        features['sttl'] = 62
    elif threat == "Brute Force":
        features['service'] = 'ssh'
        features['ct_srv_src'] = 500
        features['dur'] = 0.00001
        features['sttl'] = 254
    elif threat == "Malware Attack":
        features['sbytes'] = 150000
        features['Sjit'] = 1000
        features['stcpb'] = 987654321
    elif threat == "Data Infiltration":
        features['service'] = 'ftp'
        features['sbytes'] = 1000000
        features['dbytes'] = 500000
        features['sttl'] = 254
    elif threat == "Privilege Escalation":
        features['service'] = 'ssh'
        features['is_sm_ips_ports'] = 1
        features['sttl'] = 254
        features['sbytes'] = 20000
    elif threat == "Insider Attack":
        features['sbytes'] = 50000000
        features['dur'] = 300.0
        features['service'] = 'http'
        features['state'] = 'FIN'
        
    return features

def correlate_incidents(results):
    incidents = []
    for res in results:
        # Get safely
        ai_class = res.get('ai_class', 'Normal')
        status = res.get('status', 'normal')
        ip = res.get('ip', '0.0.0.0')
        user = res.get('user', 'N/A')
        timestamp = res.get('timestamp', '')
        is_anomaly = res.get('is_anomaly', False)

        if ai_class == "Normal" and status == "normal":
            continue
            
        found = False
        res_time = datetime.fromisoformat(timestamp.replace('Z', ''))
        
        for incident in incidents:
            ip_match = (ip == incident['ip'] and ip != '0.0.0.0')
            user_match = (user == incident['user'] and user != 'N/A')
            
            if ip_match or user_match:
                last_event_time = datetime.fromisoformat(incident['events'][-1]['timestamp'].replace('Z', ''))
                if abs((res_time - last_event_time).total_seconds()) <= 3600:
                    incident['events'].append(res)
                    incident['risk_score'] += 15 if is_anomaly else 5
                    found = True
                    break
        
        if not found:
            incidents.append({
                'ip': ip,
                'user': user,
                'risk_score': 15 if is_anomaly else 5,
                'events': [res]
            })
    return incidents

def print_investigation_report(incidents):
    if not incidents:
        print("\n✅ NO CORRELATED INCIDENTS DETECTED.")
        return

    print("\n" + "="*120)
    print(" " * 40 + "🕵️  LOGVISTA SECURITY INVESTIGATION REPORT")
    print("="*120)
    
    incidents.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
    
    for i, incident in enumerate(incidents):
        actor = incident.get('user', 'N/A') if incident.get('user', 'N/A') != 'N/A' else incident.get('ip', '0.0.0.0')
        print(f"\n🚩 INCIDENT #{i+1}: Potential Attack Campaign by [{actor}]")
        print(f"Risk Score: {incident.get('risk_score', 0)} | Total Events: {len(incident.get('events', []))}")
        print("-" * 65)
        print(f"{'TIME':<20} | {'ACTION':<35} | {'INVESTIGATION STAGE'}")
        
        for event in incident.get('events', []):
            # SAFE ACCESS
            evt_ai = event.get('ai_class', 'Unknown')
            evt_threat = event.get('threat_type', '')
            evt_time = event.get('timestamp', 'N/A')
            evt_msg = event.get('message', 'N/A')

            stage = STAGE_MAPPING.get(evt_ai, "Unknown")
            if evt_threat in SIMULATED_MAPPING:
                stage = SIMULATED_MAPPING[evt_threat]
            
            print(f"{evt_time:<20} | {evt_msg[:35]:<35} | {stage}")
        print("-" * 65)

def run_test():
    MODEL_DIR = "model"
    print("Connecting to AI Core & Loading Models...")
    try:
        rf = joblib.load(os.path.join(MODEL_DIR, 'unsw_model.pkl'), mmap_mode='r')
        iso = joblib.load(os.path.join(MODEL_DIR, 'iso_model.pkl'), mmap_mode='r')
        encoders = joblib.load(os.path.join(MODEL_DIR, 'encoders.pkl'))
        target_le = joblib.load(os.path.join(MODEL_DIR, 'target_encoder.pkl'))
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    print(f"\n{'TIMESTAMP':<20} | {'USER':<12} | {'IP':<15} | {'EVENT TYPE':<20} | {'AI RESULT'}")
    print("-" * 110)

    all_results = []

    for log in json_logs:
        network_data = simulate_network_features(log)
        df_features = prepare_features(network_data, encoders, FEATURE_COLUMNS)
        
        is_anomaly = iso.predict(df_features)[0] == -1
        pred_idx = rf.predict(df_features)[0]
        pred_class = target_le.inverse_transform([pred_idx])[0]
        
        result = pred_class
        if is_anomaly and pred_class != "Normal":
            result = f"ANOMALY ({pred_class})"
        elif is_anomaly:
            result = "ANOMALY (Unknown)"
        elif pred_class != "Normal":
            result = f"ATTACK ({pred_class})"
            
        print(f"{log.get('timestamp', 'N/A'):<20} | {log.get('user', 'N/A'):<12} | {log.get('ip', 'N/A'):<15} | {log['event_type']:<20} | {result}")
        
        res_entry = log.copy()
        res_entry['ai_class'] = pred_class
        res_entry['is_anomaly'] = is_anomaly
        all_results.append(res_entry)

    correlated_incidents = correlate_incidents(all_results)
    print_investigation_report(correlated_incidents)

if __name__ == "__main__":
    run_test()
