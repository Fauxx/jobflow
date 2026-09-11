import requests

session = requests.Session()
login = session.post("http://localhost:8001/auth/login", data={"password": "jobflow2026"})
print("Login:", login.status_code)

res = session.get("http://localhost:8001/applications/624/generate-cover-letter")
print("Response:", res.status_code)
if res.ok:
    print(res.json())
else:
    print(res.text)
