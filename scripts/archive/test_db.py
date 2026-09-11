from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileExperience, ProfileProject, ProfileSkill
from src.models.user import User

db = SessionLocal()
user = db.query(User).first()
print(f"User: {user.email}")
profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
if not profile:
    print("NO PROFILE FOUND FOR USER!")
else:
    print(f"Profile: {profile.name}, {profile.email}")
    exps = db.query(ProfileExperience).filter(ProfileExperience.profile_id == profile.id).all()
    print(f"Experiences: {len(exps)}")
    projs = db.query(ProfileProject).filter(ProfileProject.profile_id == profile.id).all()
    print(f"Projects: {len(projs)}")
    skills = db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).all()
    print(f"Skills: {len(skills)}")
