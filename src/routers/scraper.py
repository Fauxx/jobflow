from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.ingestion import IngestionService

router = APIRouter(prefix="/scrape", tags=["scraper"])

@router.post("")
async def trigger_scrape(
    keywords: str = Form(...),
    location: str = Form("Philippines"),
    db: Session = Depends(get_db)
):
    results = IngestionService.ingest_all(db, keywords, location)
    return {"status": "success", "results": results}
