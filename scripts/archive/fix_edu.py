import json
from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileEducation

with open("jobflow_backup.json", "r") as f:
    backup = json.load(f)

db = SessionLocal()
for mr in backup.get("master_resumes", []):
    content = json.loads(mr["content"])
    user_id = mr["user_id"]
    prof = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not prof: continue
    
    # Nuke existing edus just in case
    db.query(ProfileEducation).filter(ProfileEducation.profile_id == prof.id).delete()
    db.flush()
    
    for i, ed in enumerate(content.get("education", [])):
        print(f"Adding edu: {ed}")
        db.add(ProfileEducation(
            profile_id=prof.id,
            institution=ed.get("school") or ed.get("institution", ""),
            degree=ed.get("degree", ""),
            date_str=ed.get("date", ""),
            location=ed.get("location", ""),
            order=i
        ))

db.commit()
print("Education restored!")
