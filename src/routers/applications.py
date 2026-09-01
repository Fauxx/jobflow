from fastapi import APIRouter, Request, Depends, HTTPException
from src.services.ingestion import UniversalScraperService as IngestionService
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import tempfile

from fastapi.templating import Jinja2Templates
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.job import Job
from src.models.application import Application
from src.models.profile import UserProfile
from src.services.resume_tailor import ResumeTailorService

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

router = APIRouter(prefix="/applications", tags=["applications"])
templates = Jinja2Templates(directory="templates")


class ResumeUpdate(BaseModel):
    """The user's edited/approved resume data."""
    summary: str
    skills: list
    experiences: list
    projects: list
    certifications: list = []


# ─── Status Management ───


from pydantic import BaseModel
class BulkSkipRequest(BaseModel):
    job_ids: list[int]

@router.post("/bulk_skip")
async def bulk_skip(req: BulkSkipRequest, db: Session = Depends(get_db)):
    user = get_current_user(db)
    # Get existing applications for these jobs
    existing = db.query(Application).filter(
        Application.user_id == user.id,
        Application.job_id.in_(req.job_ids)
    ).all()
    
    existing_ids = {app.job_id for app in existing}
    
    # Update existing
    for app in existing:
        app.status = "SKIPPED"
        
    # Create new for those missing
    for jid in req.job_ids:
        if jid not in existing_ids:
            app = Application(job_id=jid, user_id=user.id, status="SKIPPED")
            db.add(app)
            
    db.commit()
    return {"status": "success"}

@router.post("/{job_id}/status")
async def update_status(job_id: int, status: str, db: Session = Depends(get_db)):
    user = get_current_user(db)
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()

    if not app:
        app = Application(job_id=job_id, user_id=user.id, status=status)
        db.add(app)
    else:
        app.status = status

    db.commit()
    return {"status": "success", "new_status": status}


# ─── AI Resume Builder ───

@router.get("/{job_id}/builder", response_class=HTMLResponse)
async def builder_page(request: Request, job_id: int, db: Session = Depends(get_db)):
    """The main Resume Builder page. User reviews and edits AI suggestions here."""
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # JIT Hydration: Fetch full description if missing before rendering/tailoring
    job = IngestionService.hydrate_job(db, job)

    # Get or create application
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()
    if not app:
        app = Application(job_id=job_id, user_id=user.id, status="APPROVED")
        db.add(app)
        db.commit()
        db.refresh(app)

    # Get profile for header info
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    # Check if we already have a saved resume draft
    existing_draft = None
    if app.ai_draft_json:
        try:
            existing_draft = json.loads(app.ai_draft_json)
        except Exception:
            pass

    context = {
        "request": request,
        "job": job,
        "application": app,
        "profile": profile,
        "existing_draft": json.dumps(existing_draft) if existing_draft else "null",
    }
    return templates.TemplateResponse(
        request=request, name="applications/builder.html", context=context
    )


@router.get("/{job_id}/generate")
async def generate_resume(job_id: int, db: Session = Depends(get_db)):
    """Run AI to generate tailored resume suggestions. Returns JSON for the builder UI."""
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # JIT Hydration: Fetch full description if missing before rendering/tailoring
    job = IngestionService.hydrate_job(db, job)

    # Generate tailored resume
    result = ResumeTailorService.generate_tailored_resume(db, job, user.id)

    # Save as draft
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()
    if app:
        app.ai_draft_json = json.dumps(result)
        db.commit()

    return result


@router.post("/{job_id}/save-resume")
async def save_resume(job_id: int, resume: ResumeUpdate, db: Session = Depends(get_db)):
    """Save the user's edited/approved resume."""
    user = get_current_user(db)
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Merge with existing draft (keep matched/missing skills from AI)
    existing = {}
    if app.ai_draft_json:
        try:
            existing = json.loads(app.ai_draft_json)
        except Exception:
            pass

    existing.update(resume.model_dump())
    app.ai_draft_json = json.dumps(existing)
    db.commit()
    return {"status": "success"}


# ─── Download ───

@router.get("/{job_id}/download/pdf")
async def download_pdf(request: Request, job_id: int, db: Session = Depends(get_db)):
    if not WEASYPRINT_AVAILABLE:
        return JSONResponse({"error": "WeasyPrint not installed"}, status_code=500)

    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    resume_data = json.loads(app.ai_draft_json) if app and app.ai_draft_json else {}

    html_content = templates.TemplateResponse(
        request=request,
        name="applications/resume_print.html",
        context={"request": request, "resume": resume_data, "profile": profile, "job": job}
    ).body.decode()

    tmp_pdf = tempfile.mktemp(suffix=".pdf")
    WeasyHTML(string=html_content).write_pdf(tmp_pdf)

    filename = f"Resume_{profile.name or 'Candidate'}_{job.company}.pdf".replace(" ", "_")
    return FileResponse(tmp_pdf, filename=filename, media_type="application/pdf")


@router.get("/{job_id}/download/docx")
async def download_docx(job_id: int, db: Session = Depends(get_db)):
    if not DOCX_AVAILABLE:
        return JSONResponse({"error": "python-docx not installed"}, status_code=500)

    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    app = db.query(Application).filter(
        Application.job_id == job_id, Application.user_id == user.id
    ).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    resume_data = json.loads(app.ai_draft_json) if app and app.ai_draft_json else {}

    doc = Document()

    # Header
    name = profile.name if profile else "Candidate"
    doc.add_heading(name, 0)
    contact_parts = []
    if profile:
        if profile.location: contact_parts.append(profile.location)
        if hasattr(profile, 'user_id'):
            from src.models.user import User
            u = db.query(User).filter(User.id == profile.user_id).first()
            if u: contact_parts.append(u.email)
        if profile.phone: contact_parts.append(profile.phone)
        if profile.linkedin_url: contact_parts.append(profile.linkedin_url)
        if profile.github_url: contact_parts.append(profile.github_url)
    doc.add_paragraph(" | ".join(contact_parts))

    # Summary
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(resume_data.get("summary", ""))

    # Skills
    doc.add_heading("Technical Skills", level=1)
    for cat in resume_data.get("skills", []):
        skills_str = ", ".join(cat.get("skills", []))
        doc.add_paragraph(f"{cat.get('category', '')}: {skills_str}", style="List Bullet")

    # Experience
    doc.add_heading("Professional Experience", level=1)
    for exp in resume_data.get("experiences", []):
        doc.add_heading(
            f"{exp.get('title', '')} — {exp.get('company', '')}",
            level=2
        )
        doc.add_paragraph(
            f"{exp.get('location', '')} | {exp.get('date_range', '')}"
        )
        for bullet in exp.get("bullets", []):
            text = bullet.get("tailored_text", bullet.get("original_text", ""))
            doc.add_paragraph(text, style="List Bullet")

    # Projects
    doc.add_heading("Projects", level=1)
    for proj in resume_data.get("projects", []):
        doc.add_heading(proj.get("name", ""), level=2)
        if proj.get("tech_stack"):
            doc.add_paragraph(f"Technologies: {proj['tech_stack']}")
        for bullet in proj.get("bullets", []):
            text = bullet.get("tailored_text", bullet.get("original_text", ""))
            doc.add_paragraph(text, style="List Bullet")

    # Education
    if profile and hasattr(profile, 'education') and profile.education:
        doc.add_heading("Education", level=1)
        for edu in profile.education:
            doc.add_paragraph(
                f"{edu.degree} — {edu.institution} ({edu.date_str or ''})"
            )

    tmp_docx = tempfile.mktemp(suffix=".docx")
    doc.save(tmp_docx)

    filename = f"Resume_{name}_{job.company}.docx".replace(" ", "_")
    return FileResponse(
        tmp_docx, filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.post("/empty_trash")
async def empty_trash(db: Session = Depends(get_db)):
    user = get_current_user(db)
    
    # Find all skipped applications
    skipped_apps = db.query(Application).filter(Application.user_id == user.id, Application.status == "SKIPPED").all()
    job_ids = [app.job_id for app in skipped_apps]
    
    # Delete applications
    db.query(Application).filter(Application.id.in_([a.id for a in skipped_apps])).delete(synchronize_session=False)
    
    # Delete the underlying jobs if they are no longer referenced (for safety, delete all job_ids we just found, assuming 1:1)
    if job_ids:
        db.query(Job).filter(Job.id.in_(job_ids)).delete(synchronize_session=False)
        
    db.commit()
    return {"status": "success", "deleted": len(job_ids)}
