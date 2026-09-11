import requests

s = requests.Session()
s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
resp = s.get("http://localhost:8000/profile")
print("Status:", resp.status_code)
if resp.status_code == 500:
    print(resp.text[:500])
