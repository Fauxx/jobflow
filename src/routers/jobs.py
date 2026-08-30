from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.job import Job
from src.models.application import Application
from pydantic import BaseModel
from typing import Optional
import datetime
from src.core.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobSaveRequest(BaseModel):
    external_job_id: Optional[str]
    source: str
    source_url: str
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]

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

@router.post("/{job_id}/status")
async def update_status(job_id: int, request: Request, status: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(db)
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if not app:
        app = Application(job_id=job_id, user_id=user.id, status=status)
        db.add(app)
    else:
        app.status = status
        app.updated_at = datetime.datetime.now()
    db.commit()
    return RedirectResponse(url="/", status_code=303)

