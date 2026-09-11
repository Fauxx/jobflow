import sys
import json
import uuid
import datetime
from sqlalchemy import create_engine
from src.core.config import settings
from src.models.base import Base
# Import all models so Base.metadata knows about them
from src.models.user import User
from src.models.job import Job
from src.models.application import Application
from src.models.resume import MasterResume, ResumeVersion
from src.models.profile import (
    UserProfile, ProfileExperience, ProfileProject, ProfileBullet, 
    ProfileSkill, ProfileEducation, ProfileAchievement
)
from sqlalchemy.orm import sessionmaker

def parse_dt(dt_str):
    if not dt_str: return None
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except:
        return None

engine = create_engine(settings.DATABASE_URL)
print("Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)
print("Creating new relational tables...")
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Loading backup...")
with open("jobflow_backup.json", "r") as f:
    backup = json.load(f)

print("Restoring Users...")
for u in backup.get("users", []):
    user = User(
        id=u['id'],
        email=u['email'],
        password_hash=u.get('password_hash'),
        created_at=parse_dt(u['created_at'])
    )
    db.add(user)
db.commit()

print("Restoring Jobs...")
for j in backup.get("jobs", []):
    job = Job(
        id=j['id'],
        external_job_id=j.get('external_job_id'),
        source=j.get('source', 'unknown'),
        source_url=j.get('source_url', ''),
        title=j['title'],
        company=j['company'],
        location=j['location'],
        description=j['description'],
        date_posted=parse_dt(j.get('date_posted')),
        employment_type=j.get('employment_type'),
        salary_display=j.get('salary_display'),
        workplace_type=j.get('workplace_type'),
        experience_level=j.get('experience_level'),
        raw_scraped_text=j.get('raw_scraped_text'),
        created_at=parse_dt(j['created_at']),
        scraped_at=parse_dt(j.get('scraped_at'))
    )
    db.add(job)
db.commit()

print("Restoring Applications...")
for a in backup.get("applications", []):
    app = Application(
        id=a['id'],
        job_id=a['job_id'],
        user_id=a['user_id'],
        status=a['status'],
        ai_draft_json=a.get('ai_draft_json'),
        email_subject=a.get('email_subject'),
        email_body=a.get('email_body'),
        cover_letter=a.get('cover_letter'),
        sub_status=a.get('sub_status', 'APPLIED'),
        recruiter_name=a.get('recruiter_name'),
        interview_date=parse_dt(a.get('interview_date')),
        salary_expected=a.get('salary_expected'),
        salary_offered=a.get('salary_offered'),
        pipeline_notes=a.get('pipeline_notes'),
        date_applied=parse_dt(a.get('date_applied')),
        date_screening=parse_dt(a.get('date_screening')),
        date_interview=parse_dt(a.get('date_interview')),
        date_offer=parse_dt(a.get('date_offer')),
        date_rejected=parse_dt(a.get('date_rejected')),
        created_at=parse_dt(a['created_at'])
    )
    db.add(app)
db.commit()

print("Migrating MasterResumes to SaaS Relational Structure...")
profile_map = {}
for p in backup.get("user_profiles", []):
    prof = UserProfile(
        user_id=p['user_id'],
        name=p.get('name'),
        email=p.get('email'),
        phone=p.get('phone'),
        location=p.get('location'),
        linkedin_url=p.get('linkedin_url'),
        github_url=p.get('github_url'),
        portfolio_url=p.get('portfolio_url'),
        headline=p.get('headline'),
        career_goals=p.get('career_goals'),
        target_roles=p.get('target_roles'),
        target_industries=p.get('target_industries'),
        location_prefs=p.get('location_prefs'),
        personalization_prefs=p.get('personalization_prefs')
    )
    db.add(prof)
    db.flush()
    profile_map[p['user_id']] = prof

for mr in backup.get("master_resumes", []):
    user_id = mr['user_id']
    if user_id not in profile_map:
        prof = UserProfile(user_id=user_id)
        db.add(prof)
        db.flush()
        profile_map[user_id] = prof
    
    prof = profile_map[user_id]
    
    try:
        data = json.loads(mr['content']) if mr['content'] else {}
    except:
        data = {}
        
    prof.name = data.get('name', prof.name)
    prof.location = data.get('location', prof.location)
    prof.email = data.get('email', prof.email)
    prof.phone = data.get('phone', prof.phone)
    prof.linkedin_url = data.get('linkedin', prof.linkedin_url)
    prof.github_url = data.get('github', prof.github_url)
    prof.summary = data.get('summary', prof.summary)
    
    master_ctx = data.get('master_profile', {})
    prof.master_summary_context = master_ctx.get('summary_context')
    
    for i, s in enumerate(data.get('skills', [])):
        db.add(ProfileSkill(
            profile_id=prof.id,
            category=s.get('category'),
            items=s.get('items'),
            order=i
        ))
        
    proj_contexts = {c.get('title', '').lower(): c.get('detailed_context') for c in master_ctx.get('projects', [])}
    for i, p in enumerate(data.get('projects', [])):
        title = p.get('title', '')
        proj = ProfileProject(
            profile_id=prof.id,
            title=title,
            role=p.get('role'),
            date_range=p.get('date'),
            detailed_context=proj_contexts.get(title.lower()),
            order=i
        )
        db.add(proj)
        db.flush()
        for j, b in enumerate(p.get('bullets', [])):
            if isinstance(b, dict):
                bid = b.get('id', str(uuid.uuid4()))
                btext = b.get('text', '')
            else:
                bid = str(uuid.uuid4())
                btext = b
            db.add(ProfileBullet(
                id=bid,
                project_id=proj.id,
                text=btext,
                order=j
            ))
            
    exp_contexts = {c.get('company', '').lower(): c.get('detailed_context') for c in master_ctx.get('experience', [])}
    for i, e in enumerate(data.get('experience', [])):
        company = e.get('company', '')
        exp = ProfileExperience(
            profile_id=prof.id,
            company=company,
            role=e.get('role'),
            location=e.get('location'),
            date_range=e.get('date'),
            detailed_context=exp_contexts.get(company.lower()),
            order=i
        )
        db.add(exp)
        db.flush()
        for j, b in enumerate(e.get('bullets', [])):
            if isinstance(b, dict):
                bid = b.get('id', str(uuid.uuid4()))
                btext = b.get('text', '')
            else:
                bid = str(uuid.uuid4())
                btext = b
            db.add(ProfileBullet(
                id=bid,
                experience_id=exp.id,
                text=btext,
                order=j
            ))

    # Education
    for i, ed in enumerate(data.get('education', [])):
        db.add(ProfileEducation(
            profile_id=prof.id,
            institution=ed.get('school') or ed.get('institution', ''),
            degree=ed.get('degree', ''),
            date_str=ed.get('date', ''),
            location=ed.get('location', ''),
            order=i
        ))

db.commit()
print("Success! SaaS relational migration complete.")

