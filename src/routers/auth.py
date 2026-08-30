from fastapi import APIRouter

router = APIRouter(prefix="/auth" if "auth" != "dashboard" else "", tags=["auth"])

# TODO: Add endpoints
