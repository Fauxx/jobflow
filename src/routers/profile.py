from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.services.profile_service import get_full_profile, save_full_profile

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
