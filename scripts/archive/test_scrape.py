import sys
import logging
logging.basicConfig(level=logging.INFO)
from src.core.database import SessionLocal
from src.services.ingestion import UniversalScraperService

db = SessionLocal()
try:
    url = "https://www.linkedin.com/jobs/view/4470491006/"
    print(f"Testing scraper import for: {url}")
    job = UniversalScraperService.import_job(url, db)
    print(f"Successfully imported job: {job.title}")
    print(f"Description length: {len(job.description)}")
    print(f"Gemini output preview: {job.description[:200]}")
except Exception as e:
    print(f"Failed: {e}")
finally:
    db.close()
