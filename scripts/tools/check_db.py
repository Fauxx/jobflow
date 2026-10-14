import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.database import SessionLocal
from src.models.user import User
from src.models.profile import UserProfile

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f"User: {u.email}")
profiles = db.query(UserProfile).all()
for p in profiles:
    print(f"Profile: {p.email} ({p.name})")
