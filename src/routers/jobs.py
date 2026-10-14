from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.job import Job
from src.models.application import Application
from pydantic import BaseModel
from typing import Optional
import datetime
from src.services.ingestion import UniversalScraperService as IngestionService
from src.core.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

class ManualImportRequest(BaseModel):
    title: str
    company: str
    description: Optional[str] = None

@router.post("/manual")
async def import_job_manual(req: ManualImportRequest, db: Session = Depends(get_db)):
    """Manually add a job directly to Triage inbox."""
    user = get_current_user(db)
    
    # Create the job with no url (or a dummy one to avoid constraint issues if any, but source_url is usually optional/nullable)
    job = Job(
        title=req.title,
        company=req.company,
        description=req.description,
        source="Manual",
        source_url=""
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {"status": "success", "id": job.id, "title": job.title, "company": job.company}

class JobSaveRequest(BaseModel):
    external_job_id: Optional[str] = None
    source: str
    source_url: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None

@router.post("/save")
async def save_job(job_data: JobSaveRequest, db: Session = Depends(get_db)):
    # Check if exists to be safe
    existing = db.query(Job).filter(Job.source_url == job_data.source_url).first()
    if existing:
        return {"status": "exists", "id": existing.id}
        
    job = Job(
        external_job_id=job_data.external_job_id,
        source=job_data.source,
        source_url=job_data.source_url,
        title=job_data.title,
        company=job_data.company,
        location=job_data.location,
        description=job_data.description
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Also create an application record to track status
    user = get_current_user(db)
    app = Application(
        job_id=job.id,
        user_id=user.id,
        status="APPROVED"
    )
    db.add(app)
    db.commit()
    
    return {"status": "success", "id": job.id}

@router.get("")
async def list_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Return JSON list of all jobs with status and fit scores for the React UI."""
    from src.models.profile import UserProfile
    user = get_current_user(db)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    
    # Skills for match scoring
    user_skills = set()
    if profile and profile.skills:
        for s in profile.skills:
            if s.items:
                parts = [p.strip().lower() for p in s.items.split(',')]
                for p in parts:
                    if p:
                        user_skills.add(p)
    user_skills = list(user_skills)

    # Fetch jobs with their application state for this user
    results = db.query(Job, Application).outerjoin(
        Application, (Job.id == Application.job_id) & (Application.user_id == user.id)
    ).order_by(Job.date_posted.desc().nulls_last(), Job.id.desc()).all()

    jobs_out = []
    for job, app in results:
        job_status = app.status if app else "NEW"
        if status and job_status != status:
            continue
            
        # Match score calculation
        match_score = 0
        if user_skills:
            text_to_search = f"{job.title} {job.description}".lower() if job.description else (job.title or "").lower()
            matches = sum(1 for skill in user_skills if skill in text_to_search)
            max_skills_expected = min(len(user_skills), 15)
            match_score = int(min((matches / max_skills_expected) * 100, 100)) if max_skills_expected > 0 else 0

        jobs_out.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.source_url,
            "source_platform": job.source,
            "source_job_id": job.external_job_id,
            "raw_description": job.description,
            "cleaned_description": job.description,
            "status": job_status,
            "fit_score": match_score,
            "fit_reason": f"Matches {matches} core skills from your profile" if match_score > 0 else None,
            "created_at": str(job.date_posted) if job.date_posted else None
        })

    return jobs_out

@router.post("/{job_id}/status")
async def update_status(job_id: int, request: Request, status: Optional[str] = Form(None), db: Session = Depends(get_db)):
    user = get_current_user(db)
    
    # Support both JSON payload and Form submission
    if not status:
        try:
            body = await request.json()
            status = body.get("status")
        except Exception:
            pass

    if not status:
        raise HTTPException(status_code=400, detail="Missing status")

    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if not app:
        app = Application(job_id=job_id, user_id=user.id, status=status)
        db.add(app)
    else:
        app.status = status
        app.updated_at = datetime.datetime.now()
    db.commit()

    content_type = request.headers.get("content-type", "")
    accept = request.headers.get("accept", "")
    if "application/json" in content_type or "application/json" in accept:
        return {"status": "success", "job_id": job_id, "new_status": status}

    return RedirectResponse(url="/", status_code=303)


@router.get("/{job_id}/details")
async def get_job_details(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    IngestionService.hydrate_job(db, job)
    return {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.source_url,
        "description": job.description or "",
        "source": job.source,
        "match_score": getattr(job, 'match_score', 0)
    }

class JobDetailsUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

@router.put("/{job_id}/details")
async def update_job_details(job_id: int, payload: JobDetailsUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if payload.title is not None:
        job.title = payload.title
    if payload.company is not None:
        job.company = payload.company
    if payload.location is not None:
        job.location = payload.location
    if payload.url is not None:
        job.source_url = payload.url
    if payload.description is not None:
        job.description = payload.description
        
    db.commit()
    return {"status": "success"}
