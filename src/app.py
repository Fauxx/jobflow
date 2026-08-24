import sqlite3
import json
import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict

from src.config import DB_PATH, RESUME_JSON_PATH
from src.scraper import scrape_jobs
from src.ai_engine import generate_tailored_application, suggest_resume_optimizations
from src.email_engine import send_application_email

app = FastAPI(title="Jobflow Dashboard")

# Setup templates
templates = Jinja2Templates(directory="templates")
templates.env.cache = None

class ResumeSkill(BaseModel):
    category: str
    items: str

class ResumeProject(BaseModel):
    title: str
    date: str
    role: str
    bullets: List[str]

class ResumeExperience(BaseModel):
    company: str
    location: str
    role: str
    date: str
    bullets: List[str]

class ResumeEducation(BaseModel):
    school: str
    location: str
    degree: str
    date: str

class MasterProjectContext(BaseModel):
    title: str
    detailed_context: str

class MasterExperienceContext(BaseModel):
    company: str
    detailed_context: str

class MasterProfile(BaseModel):
    summary_context: str
    projects: List[MasterProjectContext]
    experience: List[MasterExperienceContext]

class ResumeModel(BaseModel):
    name: str
    location: str
    email: str
    phone: str
    linkedin: str
    github: str
    summary: str
    skills: List[ResumeSkill]
    projects: List[ResumeProject]
    experience: List[ResumeExperience]
    education: List[ResumeEducation]
    master_profile: MasterProfile

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_resume_json():
    if os.path.exists(RESUME_JSON_PATH):
        with open(RESUME_JSON_PATH, "r") as f:
            return json.load(f)
    return {}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, status: str = "NEW", source: str = "ALL", page: int = 1):
    import math
    conn = get_db_connection()
    
    # Fetch unique sources to populate filter dropdown
    unique_sources = [r[0] for r in conn.execute("SELECT DISTINCT source FROM jobs").fetchall() if r[0]]
    
    limit = 15
    offset = (page - 1) * limit
    
    # Count total matching jobs
    if source == "ALL":
        total_jobs = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE status = ?", 
            (status,)
        ).fetchone()[0]
        
        jobs = conn.execute(
            "SELECT * FROM jobs WHERE status = ? ORDER BY discovered_date DESC LIMIT ? OFFSET ?", 
            (status, limit, offset)
        ).fetchall()
    else:
        total_jobs = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE status = ? AND source = ?", 
            (status, source)
        ).fetchone()[0]
        
        jobs = conn.execute(
            "SELECT * FROM jobs WHERE status = ? AND source = ? ORDER BY discovered_date DESC LIMIT ? OFFSET ?", 
            (status, source, limit, offset)
        ).fetchall()
        
    total_pages = max(1, math.ceil(total_jobs / limit))
        
    counts = {}
    for s in ["NEW", "APPROVED", "APPLIED", "SKIPPED"]:
        count = conn.execute("SELECT COUNT(*) FROM jobs WHERE status = ?", (s,)).fetchone()[0]
        counts[s] = count
        
    conn.close()
    
    resume = load_resume_json()
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "jobs": jobs, 
            "current_status": status, 
            "counts": counts, 
            "resume": resume,
            "unique_sources": unique_sources,
            "current_source": source,
            "page": page,
            "total_pages": total_pages
        }
    )

@app.post("/scrape")
def trigger_scrape(
    keywords: str = Form(...),
    location: str = Form(...),
    date_range: str = Form(...),
    platforms: List[str] = Form([]),
    use_auth: bool = Form(False)
):
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    scrape_jobs(keywords=keyword_list, location=location, date_range=date_range, platforms=platforms, use_auth=use_auth)
    return RedirectResponse(url=f"/?status=NEW", status_code=303)

@app.post("/jobs/{job_id}/status")
async def update_status(job_id: int, status: str = Form(...)):
    if status not in ["NEW", "SKIPPED", "APPROVED", "APPLIED"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    conn = get_db_connection()
    conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/?status={status}", status_code=303)

@app.get("/jobs/{job_id}/tailor")
def tailor_application(job_id: int):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return generate_tailored_application(job["title"], job["company"], job["description"])

@app.get("/jobs/{job_id}/tailor_resume")
def tailor_resume(job_id: int):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return suggest_resume_optimizations(job["title"], job["company"], job["description"])

@app.post("/jobs/{job_id}/apply")
def apply_job(
    job_id: int, 
    subject: str = Form(...), 
    body: str = Form(...), 
    email: str = Form(...)
):
    try:
        send_application_email(job_id, subject, body, email)
        return RedirectResponse(url="/?status=APPLIED", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resume", response_class=HTMLResponse)
async def get_resume_editor(request: Request):
    resume = load_resume_json()
    return templates.TemplateResponse(
        request=request,
        name="resume_edit.html",
        context={"resume": resume}
    )

@app.post("/resume")
async def save_resume(resume: ResumeModel):
    with open(RESUME_JSON_PATH, "w") as f:
        json.dump(resume.model_dump(), f, indent=2)
    return {"status": "success"}

@app.get("/resume/print", response_class=HTMLResponse)
async def print_resume(request: Request):
    resume = load_resume_json()
    return templates.TemplateResponse(
        request=request,
        name="resume_print.html",
        context={"resume": resume}
    )

@app.post("/resume/apply_optimization")
async def apply_optimization(opt: Dict):
    if not os.path.exists(RESUME_JSON_PATH):
        raise HTTPException(status_code=404, detail="Resume not found")
        
    with open(RESUME_JSON_PATH, "r") as f:
        resume_data = json.load(f)
        
    source = opt.get("source")
    item_idx = opt.get("item_index")
    bullet_idx = opt.get("bullet_index")
    opt_bullet = opt.get("optimized_bullet")
    
    if source == "projects":
        resume_data["projects"][item_idx]["bullets"][bullet_idx] = opt_bullet
    elif source == "experience":
        resume_data["experience"][item_idx]["bullets"][bullet_idx] = opt_bullet
        
    with open(RESUME_JSON_PATH, "w") as f:
        json.dump(resume_data, f, indent=2)
        
    return {"status": "success"}

@app.post("/launch_login")
async def launch_login(platform: str = "all"):
    import subprocess
    import sys
    try:
        # Run browser_login.py asynchronously with target platform argument
        subprocess.Popen([sys.executable, "src/browser_login.py", platform])
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/status")
def get_auth_status():
    from src.scraper import check_platform_auth
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            "linkedin": executor.submit(check_platform_auth, "linkedin"),
            "indeed": executor.submit(check_platform_auth, "indeed"),
            "jobstreet": executor.submit(check_platform_auth, "jobstreet")
        }
        return {k: v.result() for k, v in futures.items()}

@app.post("/auth/import_cookies")
def import_cookies(platform: str = Form(...), cookies_json: str = Form(...)):
    import json
    from playwright.sync_api import sync_playwright
    from src.scraper import profile_lock
    
    try:
        cookies_list = json.loads(cookies_json)
        profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "playwright_profile"))
        
        # Ensure directories exist
        os.makedirs(profile_dir, exist_ok=True)
        
        with profile_lock:
            with sync_playwright() as p:
                context = p.firefox.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=True,
                    firefox_user_prefs={
                        "dom.webdriver.enabled": False,
                        "media.peerconnection.enabled": False
                    }
                )
                
                domain_fallback = {
                    "linkedin": ".linkedin.com",
                    "indeed": ".indeed.com",
                    "jobstreet": ".jobstreet.com.ph"
                }.get(platform, "")
                
                # Format cookies correctly for Playwright
                formatted_cookies = []
                for c in cookies_list:
                    cookie = {
                        "name": c.get("name"),
                        "value": c.get("value"),
                        "domain": c.get("domain") or domain_fallback,
                        "path": c.get("path") or "/",
                    }
                    # Optional fields
                    if "expires" in c:
                        cookie["expires"] = c["expires"]
                    if "httpOnly" in c:
                        cookie["httpOnly"] = c["httpOnly"]
                    if "secure" in c:
                        cookie["secure"] = c["secure"]
                    if "sameSite" in c and c["sameSite"]:
                        val = str(c["sameSite"]).lower()
                        if val == "no_restriction" or val == "none":
                            cookie["sameSite"] = "None"
                        elif val == "lax":
                            cookie["sameSite"] = "Lax"
                        elif val == "strict":
                            cookie["sameSite"] = "Strict"
                        # If unspecified or any other value, we do not set sameSite to let Playwright use default
                        
                    formatted_cookies.append(cookie)
                        
                context.add_cookies(formatted_cookies)
                context.close()
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ScrapedJobPayload(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_time: str

@app.post("/api/import_job")
def import_job(job: ScrapedJobPayload):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check duplicate
        cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (job.title, job.company))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO jobs (title, company, location, description, description_url, contact_email, source, status, posted_time)
                VALUES (?, ?, ?, ?, ?, 'recruitment@example.com', ?, 'NEW', ?)
            """, (job.title, job.company, job.location, job.description, job.url, job.source, job.posted_time))
            conn.commit()
            print(f"User Script imported: {job.title} at {job.company}")
        return {"status": "success"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
