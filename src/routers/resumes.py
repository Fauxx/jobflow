from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/resume", tags=["resumes"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def edit_resume(request: Request):
    # Dummy resume data for MVP to prevent template undefined errors
    resume = {
        "name": "Candidate",
        "title": "Software Engineer",
        "email": "candidate@example.com",
        "phone": "+123456789",
        "location": "Remote",
        "linkedin": "linkedin.com",
        "github": "github.com",
        "portfolio": "",
        "summary": "Experienced engineer.",
        "skills": [{"category": "Languages", "items": ["Python", "JavaScript"]}],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "master_profile": {}
    }
    return templates.TemplateResponse(request=request, name="resume_edit.html", context={"request": request, "resume": resume})

@router.get("/print", response_class=HTMLResponse)
async def print_resume(request: Request):
    resume = {
        "name": "Candidate",
        "title": "Software Engineer",
        "email": "candidate@example.com",
        "phone": "+123456789",
        "location": "Remote",
        "linkedin": "linkedin.com",
        "github": "github.com",
        "summary": "Experienced engineer.",
        "skills": [{"category": "Languages", "items": ["Python"]}],
        "experience": [],
        "education": [],
        "projects": []
    }
    return templates.TemplateResponse(request=request, name="resume_print.html", context={"request": request, "resume": resume})
