import requests
import json
import uuid

BASE_URL = "http://localhost:8001"

print("--- Jobflow E2E Validation ---")

# 1. Login to get cookie
print("1. Logging in...")
session = requests.Session()
login_res = session.post(f"{BASE_URL}/auth/login", data={"password": "jobflow2026"})
if login_res.status_code != 200:
    print("LOGIN FAILED!", login_res.status_code, login_res.text)
    exit(1)
print("Login OK.")

# 2. Test Dashboard
print("2. Fetching Dashboard...")
dash_res = session.get(f"{BASE_URL}/")
if dash_res.status_code != 200:
    print("DASHBOARD FAILED!", dash_res.status_code)
    exit(1)
print("Dashboard OK.")

# 3. Create a fake Job directly to test pipeline
print("3. Creating Test Job...")
job_payload = {
    "source": "manual-test",
    "source_url": f"https://example.com/job-{uuid.uuid4()}",
    "title": "Senior AI Architect",
    "company": "DeepMind",
    "description": "Must be able to test things thoroughly."
}
job_res = session.post(f"{BASE_URL}/jobs/save", json=job_payload)
if job_res.status_code != 200:
    print("JOB CREATE FAILED!", job_res.status_code, job_res.text)
    exit(1)
job_id = job_res.json()["id"]
print(f"Job created with ID: {job_id}")

# 4. Test Manual JD Update (PUT /jobs/{id}/details)
print("4. Testing Manual JD Edit...")
jd_payload = {"description": "Updated JD via Manual Edit."}
jd_res = session.put(f"{BASE_URL}/jobs/{job_id}/details", json=jd_payload)
if jd_res.status_code != 200:
    print("JD EDIT FAILED!", jd_res.status_code, jd_res.text)
    exit(1)
print("JD Edit OK.")

# 5. Move Job to Pipeline (APPROVED) -> APPLIED and check Kanban Update
# Wait, /jobs/save already creates Application with status="APPROVED"
print("5. Moving job through Kanban Pipeline...")
# Move to APPLIED (SCREENING)
pipe_payload = {"sub_status": "SCREENING"}
pipe_res = session.put(f"{BASE_URL}/applications/{job_id}/pipeline", json=pipe_payload)
if pipe_res.status_code != 200:
    print("PIPELINE UPDATE FAILED!", pipe_res.status_code, pipe_res.text)
    exit(1)
print("Pipeline Update OK.")

# 6. Test Pipeline Details Modal Save
print("6. Testing Pipeline Details Tracker Save...")
details_payload = {
    "recruiter_name": "Demis Hassabis",
    "interview_date": "2026-09-10",
    "salary_expected": "$350,000",
    "salary_offered": "",
    "pipeline_notes": "Very exciting opportunity."
}
details_res = session.put(f"{BASE_URL}/applications/{job_id}/details", json=details_payload)
if details_res.status_code != 200:
    print("DETAILS SAVE FAILED!", details_res.status_code, details_res.text)
    exit(1)
print("Details Save OK.")

# 7. Test AI Follow-Up Generator
# (We won't actually trigger it if it causes a 429, wait let's just make sure the endpoint doesn't crash before calling Gemini)
# Actually, calling it will hit Gemini. Let's see if it works.
print("7. Testing AI Follow-up Generator (will call Gemini)...")
follow_res = session.get(f"{BASE_URL}/applications/{job_id}/generate-follow-up")
if follow_res.status_code != 200:
    print("FOLLOW UP FAILED!", follow_res.status_code, follow_res.text)
    exit(1)
print("Follow-up Generated:")
print(follow_res.json()["draft"])

print("\nALL TESTS PASSED SUCCESSFULLY! ✅")
