from utils.timeline import generate_timeline
from utils.model_handler import evaluate_log
from utils.detector import detect_log_type
import json

def test_root_hijack_reconstruction():
    print("--- Mocking ROOT HIJACK Attack Sequence ---")
    
    raw_logs = [
        "2026-04-03 10:00:01,1.2.3.4,Failed Login,High,Open,User 'root' failed to login from 1.2.3.4",
        "2026-04-03 10:00:02,1.2.3.4,Failed Login,High,Open,User 'root' failed to login from 1.2.3.4",
        "2026-04-03 10:00:03,1.2.3.4,Failed Login,High,Open,User 'root' failed to login from 1.2.3.4",
        "2026-04-03 10:01:00,1.2.3.4,Accepted Login,Info,Open,Accepted password for root from 1.2.3.4",
        "2026-04-03 10:02:00,1.2.3.4,File Access,Medium,Open,User 'root' read /etc/shadow",
        "2026-04-03 10:05:00,1.2.3.4,Exfiltration,Critical,Open,User 'root' download backup.sql"
    ]
    
    mock_events = []
    for log in raw_logs:
        ltype = detect_log_type(log)
        pred = evaluate_log(log, ltype)
        mock_events.append({
            "timestamp": log.split(',')[0],
            "ip": "1.2.3.4",
            "user": "root" if "root" in log else "N/A",
            "prediction": pred,
            "type": ltype,
            "log": log
        })
    
    result = generate_timeline(mock_events)
    
    print("\n--- Generated AI Narrative ---")
    for i, line in enumerate(result['story']):
        print(f"[{i+1}] {line}")
        
    print("\n--- Timeline Events (Stages) ---")
    for e in result['ordered_events']:
        print(f"{e['time']} | {e['phase']} | {e['attack']}")

    # Validation
    story = " ".join(result['story'])
    assert "SYSTEM HIJACK" in story, "System Hijack not detected"
    assert "DATA THEFT DETECTED" in story, "Data Theft not detected"
    assert "root" in story.lower(), "Root actor missing in story"
    
    print("\n[SUCCESS] Root Hijack forensic logic precisely verified.")

if __name__ == "__main__":
    test_root_hijack_reconstruction()
