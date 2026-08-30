import requests
import time
import sys

url = "http://127.0.0.1:8000/scrape"
data = {
    "keywords": "DevOps",
    "location": "Manila",
    "date_range": "ALL"
}

print(f"Starting E2E Scrape against {url} with data: {data}")
start_time = time.time()

try:
    response = requests.post(url, data=data, timeout=60)
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)

elapsed = time.time() - start_time

print(f"Response Status: {response.status_code}")
print(f"Elapsed Time: {elapsed:.2f} seconds")

if response.status_code == 200:
    print("Response JSON:")
    print(response.json())
    sys.exit(0)
else:
    print(f"Failed with payload: {response.text}")
    sys.exit(1)
