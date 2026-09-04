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
    from sqlalchemy.orm import outerjoin, selectinload
    profile = db.query(UserProfile).options(selectinload(UserProfile.skills)).filter(UserProfile.user_id == user.id).first()
    
    if status == "NEW":
        jobs = db.query(Job).outerjoin(Application, (Job.id == Application.job_id) & (Application.user_id == user.id))\
                 .filter((Application.id == None) | (Application.status == "NEW"))\
                 .order_by(Job.date_posted.desc().nulls_last()).all()
    else:
        results = db.query(Job, Application).join(Application).filter(
            Application.user_id == user.id,
            Application.status == status
        ).order_by(Job.date_posted.desc().nulls_last()).all()
        
        jobs = []
        for job, app in results:
            job.app_details = app
            jobs.append(job)

    # Calculate match score for ALL jobs regardless of tab
    user_skills = set()
    if profile and profile.skills:
        for s in profile.skills:
            parts = [p.strip().lower() for p in s.name.split(',')]
            for p in parts:
                if p:
                    user_skills.add(p)
    user_skills = list(user_skills)
        
    for job in jobs:
        if not user_skills:
            job.match_score = 0
            continue
            
        text_to_search = f"{job.title} {job.description}".lower() if job.description else (job.title or "").lower()
        matches = sum(1 for skill in user_skills if skill in text_to_search)
        
        max_skills_expected = min(len(user_skills), 15) 
        job.match_score = int(min((matches / max_skills_expected) * 100, 100)) if max_skills_expected > 0 else 0

    if status == "NEW":
        import datetime
        jobs.sort(key=lambda j: (j.match_score, j.date_posted.timestamp() if j.date_posted else 0), reverse=True)
        counts["NEW"] = len(jobs)
    elif status == "APPROVED":
        jobs.sort(key=lambda j: j.match_score, reverse=True)

    import datetime
    context = {
        "request": request,
        "jobs": jobs,
        "counts": counts,
        "current_status": status,
        "total_pages": 1,
        "page": 1,
        "resume": {"name": profile.name if profile else "Not set"},
        "now": datetime.datetime.now
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)
