import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.job import Job
from src.services.resume_tailor import ResumeTailorService

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jobflow:password@localhost:5432/jobflow")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Fetching generated AI draft from the database...")
from src.models.application import Application
app = db.query(Application).filter(Application.id == 229).first()
if app and app.ai_draft_json:
    resume_data = json.loads(app.ai_draft_json)
    print("\n=== SAVED DRAFT IN DATABASE ===")
    print(f"Summary: {resume_data.get('summary', '')}\n")
    
    print("Experiences mapped:")
    for exp in resume_data.get('experiences', []):
        print(f"- {exp.get('company')} ({len(exp.get('bullets', []))} bullets)")
        
    print("\nProjects mapped:")
    for proj in resume_data.get('projects', []):
        print(f"- {proj.get('title') or proj.get('name')} ({len(proj.get('bullets', []))} bullets)")
else:
    print("Draft not found in DB! Triggering generation again...")
    job = db.query(Job).filter(Job.id == 651).first()
    resume_data = ResumeTailorService.generate_tailored_resume(db, job, 1)
    
    print("\n=== AI Generation Complete ===")
    print("Summary:")
    print(resume_data.get('summary'))
    print("\nExperiences mapped:")
    for exp in resume_data.get('experiences', []):
        print(f"- {exp.get('company')} ({len(exp.get('bullets', []))} bullets)")
    print("\nProjects mapped:")
    for proj in resume_data.get('projects', []):
        print(f"- {proj.get('title') or proj.get('name')} ({len(proj.get('bullets', []))} bullets)")
