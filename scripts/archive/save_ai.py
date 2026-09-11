import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.job import Job
from src.models.application import Application
from src.services.resume_tailor import ResumeTailorService

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://jobflow:password@localhost:5432/jobflow")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Saving generated AI draft to the database...")
job = db.query(Job).filter(Job.id == 651).first()
resume_data = ResumeTailorService.generate_tailored_resume(db, job, 1)

app = db.query(Application).filter(Application.id == 229).first()
app.ai_draft_json = json.dumps(resume_data)
db.commit()
print("Saved to Application ID 229.")
