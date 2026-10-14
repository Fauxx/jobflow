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
@router.post("/import-url")
def import_job_from_url(req: ImportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        url_str = str(req.url)
        from src.models.application import Application
        from src.core.dependencies import get_current_user
        user = get_current_user(db)

        existing_job = db.query(Job).filter(Job.source_url == url_str).first()
        if existing_job:
            app = db.query(Application).filter(Application.job_id == existing_job.id, Application.user_id == user.id).first()
            if not app:
                app = Application(job_id=existing_job.id, user_id=user.id, status="SAVED")
                db.add(app)
                db.commit()
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

        # Create application with SAVED status
        app = Application(job_id=pending_job.id, user_id=user.id, status="SAVED")
        db.add(app)
        db.commit()

        # Queue the actual scrape task
        background_tasks.add_task(background_scrape_task, url_str)
        
        return {"status": "queued", "job_id": pending_job.id}
    except Exception as e:
        print(f"[Import Error] {e}")
        raise HTTPException(status_code=400, detail=str(e))
