import requests
s = requests.Session()
s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
data = {
    "name": "Zet",
    "projects": [{"title": "P1", "description": "D1", "bullets": [{"text": "B1"}]}]
}
res = s.post("http://localhost:8000/profile/", json=data)
print("Save Profile:", res.status_code)
if res.status_code != 200: print(res.text)
