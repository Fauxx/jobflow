import requests

s = requests.Session()
s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
resp = s.get("http://localhost:8000/analytics")
print("Analytics status:", resp.status_code)
if resp.status_code != 200:
    print(resp.text[:500])
