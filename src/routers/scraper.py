from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.ingestion import IngestionService

router = APIRouter(prefix="/scrape", tags=["scraper"])

@router.post("")
async def trigger_scrape(
    keywords: str = Form(...),
    location: str = Form("Philippines"),
    date_filter: str = Form("Any Time"),
    providers: str = Form(""),
    db: Session = Depends(get_db)
):
    provider_list = [p.strip() for p in providers.split(',')] if providers else None
    print(f"\n\n---> TRIGGER SCRAPE: keywords={keywords}, location={location}, date={date_filter}, providers={provider_list}\n\n")
    results = IngestionService.ingest_all(db, keywords, location, provider_list, date_filter)
    return {"status": "success", "results": results}
