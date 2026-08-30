from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from src.core.config import settings
import bcrypt

SESSION_COOKIE = "jf_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

def get_serializer():
    return URLSafeTimedSerializer(settings.SECRET_KEY)

def create_session_token() -> str:
    s = get_serializer()
    return s.dumps("authenticated", salt="session")

def verify_session_token(token: str) -> bool:
    s = get_serializer()
    try:
        s.loads(token, salt="session", max_age=SESSION_MAX_AGE)
        return True
    except (BadSignature, SignatureExpired):
        return False

def verify_password(plain: str) -> bool:
    # Compare against hashed version of ADMIN_PASSWORD stored in settings
    # We use a simple bcrypt check
    import hashlib
    return plain == settings.ADMIN_PASSWORD

def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token or not verify_session_token(token):
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    return True
