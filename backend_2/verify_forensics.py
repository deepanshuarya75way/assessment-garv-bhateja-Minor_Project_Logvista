from utils.timeline import generate_timeline
import json

def test_forensic_reconstruction():
    print("--- Mocking Multi-Stage Attack Sequence ---")
    
    mock_events = [
        {"timestamp": "2026-04-03T10:00:01", "ip": "1.2.3.4", "prediction": "Brute Force Attempt", "type": "linux_auth"},
        {"timestamp": "2026-04-03T10:00:02", "ip": "1.2.3.4", "prediction": "Brute Force Attempt", "type": "linux_auth"},
        {"timestamp": "2026-04-03T10:00:03", "ip": "1.2.3.4", "prediction": "Brute Force Attempt", "type": "linux_auth"},
        {"timestamp": "2026-04-03T10:01:00", "ip": "1.2.3.4", "prediction": "Authentication Success", "type": "auth_event"},
        {"timestamp": "2026-04-03T10:02:00", "ip": "1.2.3.4", "prediction": "Normal", "type": "file_io", "log": "read /etc/shadow"},
        {"timestamp": "2026-04-03T10:05:00", "ip": "1.2.3.4", "prediction": "File Download", "type": "file_io", "log": "download backup.sql"}
    ]
    
    result = generate_timeline(mock_events)
    
    print("\n--- Generated AI Narrative ---")
    for i, line in enumerate(result['story']):
        print(f"[{i+1}] {line}")
        
    print("\n--- Timeline Events (Stages) ---")
    for e in result['ordered_events']:
        print(f"{e['time']} | {e['phase']} | {e['attack']}")

    # Validation
    story = " ".join(result['story'])
    assert "1.2.3.4" in story, "Actor ID missing in story"
    assert "Brute Force" in story, "Brute Force not detected"
    assert "successfully gained system access" in story, "Account Takeover not detected"
    assert "DATA THEFT DETECTED" in story, "Data Theft not detected"
    
    print("\n[SUCCESS] Forensic reconstruction logic verified.")

if __name__ == "__main__":
    test_forensic_reconstruction()
