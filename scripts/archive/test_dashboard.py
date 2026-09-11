import requests
import json

s = requests.Session()
# Login
resp = s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
print("Login status:", resp.status_code)

# Get dashboard
resp = s.get("http://localhost:8000/")
print("Dashboard status:", resp.status_code)
if resp.status_code != 200:
    print(resp.text[:500])
else:
    print("Dashboard loaded successfully.")
