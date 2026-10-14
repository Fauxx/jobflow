import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.database import SessionLocal
from src.models.user import User
from src.models.profile import UserProfile

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"Updating user {u.email} -> zetsamson@gmail.com")
    u.email = "zetsamson@gmail.com"

profiles = db.query(UserProfile).all()
for p in profiles:
    print(f"Updating profile email {p.email} -> zetsamson@gmail.com")
    p.email = "zetsamson@gmail.com"

db.commit()
print("Updated successfully")
