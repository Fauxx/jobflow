from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from src.core.config import settings
from src.core.database import get_db
from sqlalchemy.orm import Session
from src.models.user import User
import bcrypt
import contextvars

SESSION_COOKIE = "jf_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# Context var to store user_id for the current request
current_user_id: contextvars.ContextVar[int] = contextvars.ContextVar("current_user_id", default=None)

def get_serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY)

def create_session_token(user_id: int) -> str:
    s = get_serializer()
    return s.dumps({"user_id": user_id}, salt="session")

def verify_session_token(token: str):
    s = get_serializer()
    try:
        payload = s.loads(token, salt="session", max_age=SESSION_MAX_AGE)
        if isinstance(payload, dict):
            return payload.get("user_id")
        return None
    except (BadSignature, SignatureExpired):
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    user_id = verify_session_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    current_user_id.set(user_id)
    return user_id

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = require_auth(request)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    return user
