import requests
import json

url = "http://127.0.0.1:5001/api/predict"

# Sample log data matching the eventlog.csv structure
payload = {
    "MachineName": "WIN-SERVER-01",
    "Category": "Network",
    "EntryType": "Warning",
    "Message": "Suspicious login attempt",
    "Source": "Security",
    "TimeGenerated": "2026-04-03 10:00:00",
    "country": "US",
    "isp": "Unknown"
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending POST request to {url}...\n")
print(f"Payload sent: \n{json.dumps(payload, indent=2)}\n")

try:
    # Send request to Flask API
    response = requests.post(url, json=payload, headers=headers)
    
    print("--- API Response ---")
    print(f"Status Code: {response.status_code}")
    
    # Try to parse the JSON response beautifully
    try:
        print(f"Response Body: \n{json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Raw Response: {response.text}")
        
except Exception as e:
    print(f"\nError! Could not connect to API. \nPlease make sure the Flask app (app.py) is running locally! \nDetails: {e}")
