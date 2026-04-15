import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_login():
    print("--- Testing Login ---")
    payload = {"username": "admin", "password": "password"}
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Login failed: {e}")

def test_upload():
    print("\n--- Testing Upload ---")
    # Sample log data (CSV style string since the parser handles it)
    log_data = "2026-04-03 10:00:00,192.168.1.100,Failed Login,High,Open,User 'admin' failed to login from 192.168.1.100"
    try:
        response = requests.post(f"{BASE_URL}/upload_logs", data=log_data, headers={'Content-Type': 'text/plain'})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Upload failed: {e}")

def test_summary():
    print("\n--- Testing Summary ---")
    try:
        response = requests.get(f"{BASE_URL}/analysis/summary")
        print(f"Status: {response.status_code}")
        summary = response.json()
        print(f"Events Count: {len(summary.get('events', []))}")
        print(f"Timeline Count: {len(summary.get('timeline', {}).get('ordered_events', []))}")
    except Exception as e:
        print(f"Summary failed: {e}")

def test_integrity():
    print("\n--- Testing Integrity ---")
    try:
        response = requests.get(f"{BASE_URL}/analysis/integrity")
        print(f"Status: {response.status_code}")
        print(f"First Hash: {response.json()[0]['hash'] if response.json() else 'None'}")
    except Exception as e:
        print(f"Integrity failed: {e}")

if __name__ == "__main__":
    test_login()
    test_upload()
    test_summary()
    test_integrity()
