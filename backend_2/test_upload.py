import requests

url = "http://127.0.0.1:5000/upload_logs"
file_path = r"c:\Project\Logvista5\logs.json"

try:
    with open(file_path, 'r') as f:
        content = f.read()
    
    response = requests.post(url, data=content, headers={"Content-Type": "text/plain"})
    print(f"Status Code: {response.status_code}")
    print("Response Content:")
    print(response.text)
except Exception as e:
    print(f"Test failed: {str(e)}")
