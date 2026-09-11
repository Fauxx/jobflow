import json
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileExperience, ProfileProject, ProfileSkill

with open("jobflow_backup.json", "r") as f:
    backup = json.load(f)

print("--- Backup Info ---")
for mr in backup.get("master_resumes", []):
    content = json.loads(mr["content"])
    print("Name:", content.get("name"))
    print("Summary length:", len(content.get("summary", "")))
    print("Experiences:", len(content.get("experience", [])))
    print("Projects:", len(content.get("projects", [])))
    print("Skills:", len(content.get("skills", [])))
    print("Education:", len(content.get("education", [])))

print("\n--- DB Info ---")
db = SessionLocal()
p = db.query(UserProfile).first()
if p:
    print("Name:", p.name)
    print("Summary length:", len(p.summary) if p.summary else 0)
    print("Experiences:", len(p.experiences))
    print("Projects:", len(p.projects))
    print("Skills:", len(p.skills))
    print("Education:", len(p.education))
else:
    print("No profile in DB")
