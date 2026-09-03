from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.ingestion import UniversalScraperService

router = APIRouter(prefix="/scrape", tags=["scraper"])

class ImportRequest(BaseModel):
    url: HttpUrl

@router.post("")
def import_job_from_url(req: ImportRequest, db: Session = Depends(get_db)):
    try:
        job = UniversalScraperService.import_job(str(req.url), db)
        return {"status": "success", "job_id": job.id, "title": job.title, "company": job.company}
    except Exception as e:
        print(f"[Import Error] {e}")
        raise HTTPException(status_code=400, detail=str(e))
