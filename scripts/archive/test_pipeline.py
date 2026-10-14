import sys
import os
import json
sys.path.append(os.path.abspath('.'))

from src.core.database import SessionLocal
from src.services.ingestion import UniversalScraperService
from src.services.job_analysis import extract_jd_requirements, extract_clean_jd
from src.services.resume_tailor import ResumeTailorService
from src.models.user import User

url = "https://www.linkedin.com/jobs/view/4468548307/"

def run():
    db = SessionLocal()
    try:
        print("1. Fetching User...")
        user = db.query(User).first()
        if not user:
            print("No user found in DB!")
            return

        print("2. Importing Job (LinkedIn)...")
        job = UniversalScraperService.import_job(url, db)
        print(f"Job imported: {job.title} (ID: {job.id})")

        print("3. Hydrating Job (Scraping Full Text)...")
        UniversalScraperService.hydrate_job(db, job)
        print(f"Job Hydrated. Text length: {len(job.raw_scraped_text) if job.raw_scraped_text else 0}")

        print("4. Analyzing Job (AI Requirement Extraction)...")
        if not job.requirements or job.requirements == "{}":
            # Extract clean JD
            if job.raw_scraped_text:
                job.description = extract_clean_jd(job.raw_scraped_text)
            
            # Extract Requirements
            reqs = extract_jd_requirements(job.description)
            job.requirements = json.dumps(reqs)
            db.commit()
            print(f"Job Analyzed. Requirements: {job.requirements}")
        else:
            print("Job already analyzed.")

        print("5. Tailoring Resume (AI Fact-Anchored Selection)...")
        tailored_data = ResumeTailorService.generate_tailored_resume(db, job, user.id)
        
        print(f"\n====================================")
        print(f"✅ PIPELINE SUCCESSFUL")
        print(f"====================================")
        print(f"Summary: {tailored_data.get('summary')}")
        print(f"Experiences Selected: {len(tailored_data.get('experiences', []))}")
        print(f"Projects Selected: {len(tailored_data.get('projects', []))}")
        print(f"Missing Skills Identified: {', '.join(tailored_data.get('missing_skills', []))}")
        
    except Exception as e:
        print(f"❌ PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

run()
