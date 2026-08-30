import os

with open('src/routers/dashboard.py', 'w') as f:
    f.write("""from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

# Assuming templates are set up in main.py
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": [], "total_jobs": 0})
""")

with open('src/routers/scraper.py', 'w') as f:
    f.write("""from fastapi import APIRouter, Request, Depends, Form
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
""")

with open('src/main.py', 'w') as f:
    f.write("""from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routers import dashboard, scraper
from src.core.config import settings
from src.core.database import engine, Base

# Base.metadata.create_all(bind=engine) # Handled by Alembic now

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(dashboard.router)
app.include_router(scraper.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
""")
