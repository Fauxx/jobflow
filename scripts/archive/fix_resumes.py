import re

with open("src/routers/resumes.py", "r") as f:
    content = f.read()

# Let's replace the top imports
content = content.replace("from src.models.resume import MasterResume\n", "")
new_imports = """from src.models.profile import UserProfile, ProfileSkill, ProfileProject, ProfileExperience, ProfileBullet, ProfileEducation
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
"""

# Inject before router = APIRouter...
content = content.replace("router = APIRouter(prefix=\"/resume\", tags=[\"resumes\"])", new_imports + "\nrouter = APIRouter(prefix=\"/resume\", tags=[\"resumes\"])")

# Now rewrite edit_resume:
old_edit = """async def edit_resume(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)
    mr = db.query(MasterResume).filter(MasterResume.user_id == user.id).first()
    
    if mr:
        resume_data = json.loads(mr.content)
    else:
        # Fallback to local resume.json
        try:
            with open("src/resume.json", "r") as f:
                resume_data = json.load(f)
        except Exception:
            resume_data = {}
            
    return templates.TemplateResponse(request=request, name="resume_edit.html", context={"request": request, "resume": resume_data})"""

new_edit = """async def edit_resume(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)
    resume_data = get_legacy_resume_dict(db, user.id)
    if not resume_data:
        try:
            with open("src/resume.json", "r") as f:
                resume_data = json.load(f)
        except Exception:
            resume_data = {}
    return templates.TemplateResponse(request=request, name="resume_edit.html", context={"request": request, "resume": resume_data})"""

content = content.replace(old_edit, new_edit)

# Rewrite builder mr read
content = content.replace("mr = db.query(MasterResume).filter(MasterResume.user_id == user.id).first()\n    master_profile = json.loads(mr.content) if mr and mr.content else {}", "master_profile = get_legacy_resume_dict(db, user.id)")

# Rewrite save_resume
old_save = """async def save_resume(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = get_current_user(db)
    mr = db.query(MasterResume).filter(MasterResume.user_id == user.id).first()
    
    if not mr:
        mr = MasterResume(user_id=user.id, format="json", content=json.dumps(data))
        db.add(mr)
    else:
        mr.content = json.dumps(data)
        
    db.commit()
    return {"status": "success"}"""

new_save = """async def save_resume(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = get_current_user(db)
    save_legacy_resume_dict(db, user.id, data)
    return {"status": "success"}"""

content = content.replace(old_save, new_save)

# Rewrite print and downloads
content = content.replace("mr = db.query(MasterResume).filter(MasterResume.user_id == user.id).first()\n    resume_data = json.loads(mr.content) if mr else {}", "resume_data = get_legacy_resume_dict(db, user.id)")

with open("src/routers/resumes.py", "w") as f:
    f.write(content)
