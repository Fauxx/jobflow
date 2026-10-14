import re
import uuid
from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileProject, ProfileBullet

db = SessionLocal()
profile = db.query(UserProfile).first()
if not profile:
    print("No profile")
    exit(1)

project = None
for p in profile.projects:
    if "Fire Monitoring System" in p.title:
        project = p
        break

if not project:
    print("Project not found")
    exit(1)

# Delete existing bullets
db.query(ProfileBullet).filter(ProfileBullet.project_id == project.id).delete()
db.commit()

# Read the md file
with open('/home/zett/RiderProjects/FireMonitoringSystem/RESUME_ARCHITECTURE_NOTES.md', 'r') as f:
    content = f.read()

bullets = []
for line in content.split('\n'):
    line = line.strip()
    if line.startswith('* "') and line.endswith('"'):
        bullet_text = line[3:-1]
        bullets.append(bullet_text)

print(f"Extracted {len(bullets)} bullets")

for i, text in enumerate(bullets):
    b = ProfileBullet(
        id=str(uuid.uuid4()),
        project_id=project.id,
        text=text,
        order=i
    )
    db.add(b)

db.commit()
print("Updated successfully!")
