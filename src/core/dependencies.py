from fastapi import Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.user import User
from src.models.profile import UserProfile

def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, email="candidate@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, name="Candidate (Default)", title="Software Engineer")
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    return user
