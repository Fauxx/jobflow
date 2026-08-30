from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.models.job import Job
from src.models.application import Application
from src.models.profile import UserProfile
from src.core.dependencies import get_current_user

router = APIRouter(tags=["dashboard"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, status: str = "NEW", db: Session = Depends(get_db)):
    user = get_current_user(db)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    
    # Calculate counts
    # NEW is ephemeral now, so we'll just set it to 0 or leave it for the UI to override
    counts = {"NEW": 0, "APPROVED": 0, "APPLIED": 0, "SKIPPED": 0}
    status_counts = db.query(Application.status, func.count(Application.id)).filter(Application.user_id == user.id).group_by(Application.status).all()
    for st, count in status_counts:
        counts[st] = count

    # Fetch jobs for the selected status
    if status == "NEW":
        # Jobs that have no application for this user, or application status is NEW
        from sqlalchemy.orm import outerjoin
        jobs = db.query(Job).outerjoin(Application, (Job.id == Application.job_id) & (Application.user_id == user.id))\
                 .filter((Application.id == None) | (Application.status == "NEW"))\
                 .order_by(Job.date_posted.desc().nulls_last()).all()
        counts["NEW"] = len(jobs)
    else:
        jobs = db.query(Job).join(Application).filter(
            Application.user_id == user.id,
            Application.status == status
        ).order_by(Job.date_posted.desc().nulls_last()).all()

    context = {
        "request": request,
        "jobs": jobs,
        "counts": counts,
        "current_status": status,
        "total_pages": 1,
        "page": 1,
        "resume": {"name": profile.name if profile else "Not set"}
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)
