from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
import tempfile

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.services.profile_service import get_full_profile, save_full_profile
from src.models.profile import UserProfile, ProfileProject, ProfileExperience
from sqlalchemy import orm

try:
    from weasyprint import HTML as WeasyprintHTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def view_profile(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    profile_data = get_full_profile(db, current_user.id)
    return templates.TemplateResponse(request=request, name="profile/view.html", context={"request": request, "profile": profile_data})

@router.post("/")
async def update_profile(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        profile_data = await request.json()
        save_full_profile(db, current_user.id, profile_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import")
async def import_profile(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        with open("src/resume.json", "r") as f:
            resume = json.load(f)
            
        profile_data = {
            "name": resume.get("name"),
            "location": resume.get("location"),
            "phone": resume.get("phone"),
            "linkedin_url": resume.get("linkedin"),
            "github_url": resume.get("github"),
            "headline": resume.get("summary", "")[:200],
            "career_goals": resume.get("summary"),
            "skills": [],
            "projects": [],
            "experiences": [],
            "education": []
        }
        
        for skill in resume.get("skills", []):
            profile_data["skills"].append({
                "category": skill.get("category"),
                "name": skill.get("items")
            })
            
        for i, proj in enumerate(resume.get("projects", [])):
            profile_data["projects"].append({
                "name": proj.get("title"),
                "date_range": proj.get("date"),
                "role": proj.get("role"),
                "order": i,
                "is_highlight": True,
                "bullets": [{"raw_text": b} for b in proj.get("bullets", [])]
            })
            
        for i, exp in enumerate(resume.get("experience", [])):
            profile_data["experiences"].append({
                "company": exp.get("company"),
                "location": exp.get("location"),
                "title": exp.get("role"),
                "start_date": exp.get("date"),
                "order": i,
                "bullets": [{"raw_text": b} for b in exp.get("bullets", [])]
            })
            
        for edu in resume.get("education", []):
            profile_data["education"].append({
                "institution": edu.get("school"),
                "location": edu.get("location"),
                "degree": edu.get("degree"),
                "date_str": edu.get("date")
            })
            
        save_full_profile(db, current_user.id, profile_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/preview", response_class=HTMLResponse)
async def preview_profile(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Render a rich, portfolio-style HTML preview of the Master Profile from DB."""
    profile = db.query(UserProfile).options(
        orm.selectinload(UserProfile.skills),
        orm.selectinload(UserProfile.projects).selectinload(ProfileProject.bullets),
        orm.selectinload(UserProfile.experiences).selectinload(ProfileExperience.bullets),
        orm.selectinload(UserProfile.education),
        orm.selectinload(UserProfile.achievements),
    ).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        return HTMLResponse("<h1>No profile found. <a href='/profile/'>Create one here</a>.</h1>", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="profile/preview.html",
        context={"request": request, "profile": profile}
    )


@router.get("/preview/pdf")
async def preview_profile_pdf(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Generate and download a PDF version of the Master Profile preview."""
    if not WEASYPRINT_AVAILABLE:
        raise HTTPException(status_code=501, detail="WeasyPrint is not installed.")

    profile = db.query(UserProfile).options(
        orm.selectinload(UserProfile.skills),
        orm.selectinload(UserProfile.projects).selectinload(ProfileProject.bullets),
        orm.selectinload(UserProfile.experiences).selectinload(ProfileExperience.bullets),
        orm.selectinload(UserProfile.education),
        orm.selectinload(UserProfile.achievements),
    ).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="No profile found.")

    html_content = templates.TemplateResponse(
        request=request,
        name="profile/preview.html",
        context={"request": request, "profile": profile}
    ).body.decode()

    tmp_pdf = tempfile.mktemp(suffix=".pdf")
    WeasyprintHTML(string=html_content, base_url=str(request.base_url)).write_pdf(tmp_pdf)

    filename = f"{(profile.name or 'Profile').replace(' ', '_')}_MasterProfile.pdf"
    return FileResponse(tmp_pdf, filename=filename, media_type="application/pdf")
