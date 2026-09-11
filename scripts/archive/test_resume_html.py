import requests
s = requests.Session()
s.post("http://localhost:8000/auth/login", data={"email": "admin@jobflow.com", "password": "jobflow2026"})
resp = s.get("http://localhost:8000/resume")
print("Response text snippet:", resp.text[1500:2500])
with open("dump.html", "w") as f:
    f.write(resp.text)
