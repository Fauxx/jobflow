from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.user import User
from src.core.auth import current_user_id

def get_current_user(db: Session = Depends(get_db)) -> User:
    user_id = current_user_id.get()
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user
