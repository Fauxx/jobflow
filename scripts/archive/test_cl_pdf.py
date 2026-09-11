import requests

session = requests.Session()
login = session.post("http://localhost:8001/auth/login", data={"password": "jobflow2026"})
print("Login:", login.status_code)

payload = {"content": "Dear hiring manager,\nI am writing to apply for the Senior AI Architect role."}
res = session.post("http://localhost:8001/applications/624/cover-letter/pdf", json=payload)
print("Response:", res.status_code)
if res.ok:
    print("PDF size:", len(res.content))
else:
    print(res.text)
