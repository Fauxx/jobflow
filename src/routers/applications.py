from fastapi import APIRouter

router = APIRouter(prefix="/applications" if "applications" != "dashboard" else "", tags=["applications"])

# TODO: Add endpoints
