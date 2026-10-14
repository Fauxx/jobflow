from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
import os
import tempfile
from docx import Document

from src.core.database import get_db
from src.core.dependencies import get_current_user

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from src.models.profile import UserProfile, ProfileSkill, ProfileProject, ProfileExperience, ProfileBullet, ProfileEducation
import uuid

def get_legacy_resume_dict(db: Session, user_id: int):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile: return {}
    
    data = {
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "linkedin": profile.linkedin_url,
        "github": profile.github_url,
        "summary": profile.summary,
        "skills": [],
        "projects": [],
        "experience": [],
        "education": [],
        "master_profile": {"summary_context": profile.master_summary_context, "projects": [], "experience": []}
    }
    
    for s in sorted(profile.skills, key=lambda x: x.order):
        data["skills"].append({"category": s.category, "items": s.items})
        
    for p in sorted(profile.projects, key=lambda x: x.order):
        proj = {
            "title": p.title,
            "role": p.role,
            "date": p.date_range,
            "bullets": [{"id": str(b.id), "text": b.text} for b in sorted(p.bullets, key=lambda x: x.order)]
        }
        data["projects"].append(proj)
        data["master_profile"]["projects"].append({"title": p.title, "detailed_context": p.detailed_context})
        
    for e in sorted(profile.experiences, key=lambda x: x.order):
        exp = {
            "company": e.company,
            "role": e.role,
            "location": e.location,
            "date": e.date_range,
            "bullets": [{"id": str(b.id), "text": b.text} for b in sorted(e.bullets, key=lambda x: x.order)]
        }
        data["experience"].append(exp)
        data["master_profile"]["experience"].append({"company": e.company, "detailed_context": e.detailed_context})
        
    for ed in sorted(profile.education, key=lambda x: x.order):
        data["education"].append({"school": ed.institution, "degree": ed.degree, "date": ed.date_str, "location": ed.location})
        
    return data

def save_legacy_resume_dict(db: Session, user_id: int, data: dict):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.flush()
        
    profile.name = data.get("name")
    profile.email = data.get("email")
    profile.phone = data.get("phone")
    profile.location = data.get("location")
    profile.linkedin_url = data.get("linkedin")
    profile.github_url = data.get("github")
    profile.summary = data.get("summary")
    
    master_profile = data.get("master_profile", {})
    if isinstance(master_profile, dict):
        profile.master_summary_context = master_profile.get("summary_context")
    else:
        master_profile = {}
    
    db.query(ProfileSkill).filter(ProfileSkill.profile_id == profile.id).delete()
    db.query(ProfileProject).filter(ProfileProject.profile_id == profile.id).delete()
    db.query(ProfileExperience).filter(ProfileExperience.profile_id == profile.id).delete()
    db.query(ProfileEducation).filter(ProfileEducation.profile_id == profile.id).delete()
    db.flush()
    
    for i, s in enumerate(data.get("skills", [])):
        db.add(ProfileSkill(profile_id=profile.id, category=s.get("category"), items=s.get("items"), order=i))
        
    proj_contexts = {p.get("title", "").lower(): p.get("detailed_context") for p in master_profile.get("projects", [])} if master_profile else {}
    for i, p in enumerate(data.get("projects", [])):
        proj = ProfileProject(
            profile_id=profile.id,
            title=p.get("title"),
            role=p.get("role"),
            date_range=p.get("date"),
            detailed_context=proj_contexts.get(p.get("title", "").lower()),
            order=i
        )
        db.add(proj)
        db.flush()
        for j, b in enumerate(p.get("bullets", [])):
            text = b.get("text") if isinstance(b, dict) else b
            bid = b.get("id", str(uuid.uuid4())) if isinstance(b, dict) else str(uuid.uuid4())
            db.add(ProfileBullet(id=bid, project_id=proj.id, text=text, order=j))
            
    exp_contexts = {e.get("company", "").lower(): e.get("detailed_context") for e in master_profile.get("experience", [])} if master_profile else {}
    for i, e in enumerate(data.get("experience", [])):
        exp = ProfileExperience(
            profile_id=profile.id,
            company=e.get("company"),
            role=e.get("role"),
            location=e.get("location"),
            date_range=e.get("date"),
            detailed_context=exp_contexts.get(e.get("company", "").lower()),
            order=i
        )
        db.add(exp)
        db.flush()
        for j, b in enumerate(e.get("bullets", [])):
            text = b.get("text") if isinstance(b, dict) else b
            bid = b.get("id", str(uuid.uuid4())) if isinstance(b, dict) else str(uuid.uuid4())
            db.add(ProfileBullet(id=bid, experience_id=exp.id, text=text, order=j))
            
    for i, ed in enumerate(data.get("education", [])):
        db.add(ProfileEducation(
            profile_id=profile.id,
            institution=ed.get("school"),
            degree=ed.get("degree"),
            date_str=ed.get("date"),
            location=ed.get("location"),
            order=i
        ))
        
    db.commit()

router = APIRouter(prefix="/resume", tags=["resumes"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def edit_resume(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)
    resume_data = get_legacy_resume_dict(db, user.id)
    if not resume_data:
        try:
            with open("src/resume.json", "r") as f:
                resume_data = json.load(f)
        except Exception:
            resume_data = {}
    return templates.TemplateResponse(request=request, name="resume_edit.html", context={"request": request, "resume": resume_data})

from src.models.job import Job
from src.models.application import Application
from src.services.job_analysis import extract_clean_jd
from src.services.resume_tailor import ResumeTailorService

def background_tailor_task(job_id: int, user_id: int):
    from src.core.database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user_id).first()
        if not job or not app:
            return
            
        if not job.description or "[AI Extraction Pending]" in job.description:
            if job.raw_scraped_text:
                job.description = extract_clean_jd(job.raw_scraped_text)
                db.commit()
                
        if not app.ai_draft_json:
            tailored_data = ResumeTailorService.generate_tailored_resume(db, job, user_id)
            app.ai_draft_json = json.dumps(tailored_data)
            db.commit()
    except Exception as e:
        print(f"Error in background_tailor_task: {e}")
    finally:
        db.close()

@router.post("/builder/{job_id}/tailor-async")
async def trigger_tailor_async(job_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404)
        
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if not app:
        app = Application(job_id=job.id, user_id=user.id, status="APPROVED")
        db.add(app)
        db.commit()
    elif app.status in ["NEW", "SKIPPED"]:
        app.status = "APPROVED"
        db.commit()
        
    background_tasks.add_task(background_tailor_task, job_id, user.id)
    return {"status": "queued"}

@router.get("/builder/{job_id}", response_class=HTMLResponse)
async def builder(request: Request, job_id: int, db: Session = Depends(get_db)):
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        return HTMLResponse("Job not found", status_code=404)
        
    # Auto-Approve Job if not already applied/approved
    app = db.query(Application).filter(Application.job_id == job.id, Application.user_id == user.id).first()
    if not app:
        app = Application(job_id=job.id, user_id=user.id, status="APPROVED")
        db.add(app)
        db.commit()
    elif app.status == "NEW" or app.status == "SKIPPED":
        app.status = "APPROVED"
        db.commit()
        
    # Extract clean JD if not done already
    if not job.description or "[AI Extraction Pending]" in job.description:
        if job.raw_scraped_text:
            job.description = extract_clean_jd(job.raw_scraped_text)
            db.commit()
            
    # Tailor resume - Cache it to save API quota!
    if app.ai_draft_json:
        tailored_data = json.loads(app.ai_draft_json)
    else:
        tailored_data = ResumeTailorService.generate_tailored_resume(db, job, user.id)
        app.ai_draft_json = json.dumps(tailored_data)
        db.commit()
    
    master_profile = get_legacy_resume_dict(db, user.id)

    return templates.TemplateResponse(request=request, name="builder.html", context={
        "request": request, 
        "job": job, 
        "tailored_resume": tailored_data,
        "master_profile": master_profile
    })

@router.post("/builder/{job_id}/regenerate")
async def regenerate_builder(job_id: int, db: Session = Depends(get_db)):
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    app = db.query(Application).filter(Application.job_id == job.id, Application.user_id == user.id).first()
    
    if not job or not app:
        raise HTTPException(status_code=404, detail="Job or Application not found")
        
    tailored_data = ResumeTailorService.generate_tailored_resume(db, job, user.id)
    app.ai_draft_json = json.dumps(tailored_data)
    db.commit()
    
    return {"status": "success"}

@router.post("/builder/{job_id}/save")
async def save_builder(job_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    
    if not app:
        return {"status": "error", "message": "Application not found"}
        
    data = await request.json()
    app.ai_draft_json = json.dumps(data)
    db.commit()
    
    return {"status": "success"}

from pydantic import BaseModel
class AdjustRequest(BaseModel):
    instruction: str

@router.post("/builder/{job_id}/adjust")
async def adjust_resume_with_ai(job_id: int, req: AdjustRequest, db: Session = Depends(get_db)):
    from src.services.resume_tailor import ResumeTailorService
    from fastapi import HTTPException
    
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    
    if not job or not app:
        raise HTTPException(status_code=404, detail="Job or Application not found")
        
    current_draft = json.loads(app.ai_draft_json) if app.ai_draft_json else {}
    
    updated_draft = ResumeTailorService.adjust_resume(db, job, user.id, current_draft, req.instruction)
    app.ai_draft_json = json.dumps(updated_draft)
    db.commit()
    
    return {"status": "success"}

class AdjustSummaryRequest(BaseModel):
    instruction: str
    current_summary: str

@router.post("/builder/{job_id}/adjust-summary")
async def adjust_summary_with_ai(job_id: int, req: AdjustSummaryRequest, db: Session = Depends(get_db)):
    from src.services.resume_tailor import ResumeTailorService
    from fastapi import HTTPException
    
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    new_summary = ResumeTailorService.adjust_summary(db, job, user.id, req.current_summary, req.instruction)
    
    # Let's save it directly to the draft as well
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if app and app.ai_draft_json:
        try:
            draft = json.loads(app.ai_draft_json)
            draft['summary'] = new_summary.strip()
            app.ai_draft_json = json.dumps(draft)
            db.commit()
        except:
            pass

    return {"summary": new_summary.strip()}

class AdjustSkillsRequest(BaseModel):
    instruction: str
    current_skills: list

@router.post("/builder/{job_id}/adjust-skills")
async def adjust_skills_with_ai(job_id: int, req: AdjustSkillsRequest, db: Session = Depends(get_db)):
    from src.services.resume_tailor import ResumeTailorService
    from fastapi import HTTPException
    
    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    new_skills = ResumeTailorService.adjust_skills(db, job, user.id, req.current_skills, req.instruction)
    
    # Let's save it directly to the draft as well
    app = db.query(Application).filter(Application.job_id == job_id, Application.user_id == user.id).first()
    if app and app.ai_draft_json:
        try:
            draft = json.loads(app.ai_draft_json)
            draft['skills'] = new_skills
            app.ai_draft_json = json.dumps(draft)
            db.commit()
        except:
            pass

    return {"skills": new_skills}

class AdjustSectionRequest(BaseModel):
    section_type: str  # "experience" or "project"
    section_name: str  # company name or project name (to identify which one)
    instruction: str
    current_bullets: list  # list of bullet text strings currently in the card

@router.post("/builder/{job_id}/adjust-section")
async def adjust_section_with_ai(job_id: int, req: AdjustSectionRequest, db: Session = Depends(get_db)):
    """Regenerate bullets for a specific experience or project card with a custom instruction."""
    from src.services.job_analysis import call_gemini
    from src.services.context_builder import build_context

    user = get_current_user(db)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidate_context = build_context(db, job, user.id)

    prompt = f"""You are a Fact-Anchored Resume Curator Engine helping tailor specific resume bullets.

STRICT RULES:
1. Only select bullets from the CANDIDATE KNOWLEDGE BASE. Do NOT invent anything.
2. Return bullets verbatim (exact text) — do NOT rephrase or rewrite.
3. Return exactly 3 to 5 bullets.
4. Follow the user's instruction carefully.

## JOB BEING APPLIED TO
Title: {job.title}
Company: {job.company}

## SECTION TO UPDATE
Type: {req.section_type}
Name: {req.section_name}

## USER INSTRUCTION
"{req.instruction}"

## CURRENT BULLETS IN THIS CARD
{json.dumps(req.current_bullets, indent=2)}

## FULL CANDIDATE KNOWLEDGE BASE
{candidate_context}

## YOUR TASK
Re-select 3-5 bullets for the "{req.section_name}" {req.section_type} section based on the user's instruction.
Look through ALL bullets available for this section in the Knowledge Base and apply the user's instruction.

Return ONLY a JSON array of bullet objects like this:
[
  {{
    "id": "exact bullet UUID from the knowledge base",
    "original_text": "exact verbatim text from knowledge base",
    "tailored_text": "exact verbatim text (IDENTICAL to original_text)",
    "highly_recommended": true,
    "reason": "brief reason"
  }}
]

Output ONLY the JSON array. No markdown, no explanations.
"""

    try:
        resp = call_gemini(prompt).strip()
        if resp.startswith("```"):
            resp = resp.split("```json", 1)[-1].rsplit("```", 1)[0].strip() if "```json" in resp else resp.split("```", 1)[1].rsplit("```", 1)[0].strip()
        bullets = json.loads(resp)
        if not isinstance(bullets, list):
            raise ValueError("Expected a JSON array")
        return {"bullets": bullets}
    except Exception as e:
        print(f"[adjust-section] AI failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI adjustment failed: {str(e)}")

@router.post("")
async def save_resume(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = get_current_user(db)
    save_legacy_resume_dict(db, user.id, data)
    return {"status": "success"}

@router.get("/print", response_class=HTMLResponse)
async def print_resume(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)
    resume_data = get_legacy_resume_dict(db, user.id)
    return templates.TemplateResponse(request=request, name="resume_print.html", context={"request": request, "resume": resume_data})

@router.get("/download/pdf")
async def download_pdf(request: Request, db: Session = Depends(get_db)):
    if not WEASYPRINT_AVAILABLE:
        return {"error": "WeasyPrint not installed"}
        
    user = get_current_user(db)
    resume_data = get_legacy_resume_dict(db, user.id)
    
    html_content = templates.TemplateResponse("resume_print.html", {"request": request, "resume": resume_data}).body.decode()
    
    tmp_pdf = tempfile.mktemp(suffix=".pdf")
    HTML(string=html_content, base_url=str(request.base_url)).write_pdf(tmp_pdf)
    
    return FileResponse(tmp_pdf, filename="Resume.pdf", media_type="application/pdf")

@router.get("/download/docx")
async def download_docx(db: Session = Depends(get_db)):
    user = get_current_user(db)
    resume_data = get_legacy_resume_dict(db, user.id)
    
    doc = Document()
    doc.add_heading(resume_data.get("name", "Candidate"), 0)
    
    contact = f"{resume_data.get('location', '')} | {resume_data.get('email', '')} | {resume_data.get('phone', '')}"
    doc.add_paragraph(contact)
    
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(resume_data.get("summary", ""))
    
    doc.add_heading("Skills", level=1)
    for s in resume_data.get("skills", []):
        doc.add_paragraph(f"{s.get('category')}: {s.get('items')}", style="List Bullet")
        
    doc.add_heading("Experience", level=1)
    for e in resume_data.get("experience", []):
        doc.add_heading(f"{e.get('company')} - {e.get('role')}", level=2)
        doc.add_paragraph(e.get('date', ''))
        for b in e.get('bullets', []):
            doc.add_paragraph(b, style="List Bullet")
            
    doc.add_heading("Projects", level=1)
    for p in resume_data.get("projects", []):
        doc.add_heading(p.get('title'), level=2)
        for b in p.get('bullets', []):
            doc.add_paragraph(b, style="List Bullet")
            
    doc.add_heading("Education", level=1)
    for edu in resume_data.get("education", []):
        doc.add_heading(edu.get('school'), level=2)
        doc.add_paragraph(f"{edu.get('degree')} - {edu.get('date')}")
        
    tmp_docx = tempfile.mktemp(suffix=".docx")
    doc.save(tmp_docx)
    
    return FileResponse(tmp_docx, filename="Resume.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
