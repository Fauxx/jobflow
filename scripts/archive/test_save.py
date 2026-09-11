import requests
import json

s = requests.Session()
s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
resp = s.get("http://localhost:8000/resume")

# Just try to post a dummy dict
data = {
    "name": "Zet Donaue Samson",
    "email": "zetsamson@gmail.com",
    "projects": [{"title": "Test Proj", "role": "Dev", "date": "2024", "bullets": [{"id": "xyz", "text": "test bullet"}]}]
}
res = s.post("http://localhost:8000/resume", json=data)
print("Save status:", res.status_code)
if res.status_code != 200:
    print(res.text)
