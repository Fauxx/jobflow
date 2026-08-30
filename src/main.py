from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routers import dashboard, scraper, profile, jobs, resumes
from src.core.config import settings
from src.core.database import engine
from src.models import Base

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(scraper.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(resumes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
