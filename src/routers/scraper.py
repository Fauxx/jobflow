from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.ingestion import UniversalScraperService
from urllib.parse import urlparse

router = APIRouter(prefix="/scrape", tags=["scraper"])

class ImportRequest(BaseModel):
    url: HttpUrl

def background_scrape_task(url: str):
    # We must create a new DB session for the background task to avoid threading issues
    from src.core.database import SessionLocal
    db = SessionLocal()
    try:
        # Call the existing sync logic, but inside the background task
        UniversalScraperService.import_job(url, db)
    except Exception as e:
        print(f"[Background Scrape Error] {e}")
    finally:
        db.close()

@router.post("")
def import_job_from_url(req: ImportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        url_str = str(req.url)
        # Fast check if it already exists before queuing
        from src.models.job import Job
        existing_job = db.query(Job).filter(Job.source_url == url_str).first()
        if existing_job:
            return {"status": "success", "message": "Already imported", "job_id": existing_job.id}
        
        # Add a placeholder "Pending" job instantly to the DB so the UI sees it
        domain = urlparse(url_str).netloc.replace('www.', '')
        pending_job = Job(
            title="[Pending AI Extraction] " + domain,
            company=domain.capitalize(),
            location="Unspecified",
            description="Scraping in progress... this will update automatically.",
            raw_scraped_text="",
            source=domain,
            source_url=url_str
        )
        db.add(pending_job)
        db.commit()
        db.refresh(pending_job)

        # Queue the actual scrape task
        background_tasks.add_task(background_scrape_task, url_str)
        
        return {"status": "queued", "job_id": pending_job.id}
    except Exception as e:
        print(f"[Import Error] {e}")
        raise HTTPException(status_code=400, detail=str(e))
