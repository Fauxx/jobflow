import sys
from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileProject, ProfileExperience, ProfileBullet

db = SessionLocal()
profile = db.query(UserProfile).first()
if not profile:
    print("No profile found.")
    sys.exit(0)

print(f"Profile: {profile.name} - {profile.title}")
print("\nProjects:")
for proj in profile.projects:
    print(f" - {proj.id}: {proj.name}")

print("\nExperiences:")
for exp in profile.experiences:
    print(f" - {exp.id}: {exp.company} - {exp.title}")
