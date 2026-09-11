import sys, json
sys.path.append('/home/zett/RiderProjects/jobflow')
from src.core.database import SessionLocal
from src.models.job import Job
from src.models.application import Application
from src.services.resume_tailor import ResumeTailorService
from src.services.ingestion import UniversalScraperService

db = SessionLocal()

# find a job that has a URL
job = db.query(Job).filter(Job.source_url.isnot(None)).first()
if job:
    print(f"Testing on Job: {job.title}")
    UniversalScraperService.hydrate_job(db, job)
    print("Hydration successful.")
    
    res = ResumeTailorService.generate_tailored_resume(db, job, 1) # Assuming user_id=1
    print("AI Resume Result keys:", res.keys())
    print("Summary:", res.get("summary"))
    print("Experiences count:", len(res.get("experiences", [])))
else:
    print("No job found in DB to test.")
