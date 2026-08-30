from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from src.routers import dashboard, scraper, profile, jobs, resumes, auth
try:
    from src.routers import applications
    has_applications = True
except Exception:
    has_applications = False
from src.core.config import settings
from src.core.database import engine
from src.models import Base
from src.core.auth import require_auth

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Auth router — no protection needed
app.include_router(auth.router)

# Protected routers
protected = {"dependencies": [Depends(require_auth)]}
app.include_router(dashboard.router, **protected)
app.include_router(scraper.router, **protected)
app.include_router(profile.router, **protected)
app.include_router(jobs.router, **protected)
app.include_router(resumes.router, **protected)
if has_applications:
    app.include_router(applications.router, **protected)

@app.get("/health")
def health_check():
    return {"status": "ok"}
