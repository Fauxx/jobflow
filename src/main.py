from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from src.routers import dashboard, scraper, profile, jobs, resumes, auth, applications
from src.core.config import settings
from src.core.database import engine
from src.models import Base
from src.core.auth import verify_session_token, SESSION_COOKIE

app = FastAPI(title=settings.PROJECT_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Auth middleware — redirect unauthenticated users to login
PUBLIC_PATHS = {"/auth/login", "/auth/logout", "/health", "/openapi.json", "/docs", "/redoc"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # Allow public paths and static files
    if path.startswith("/static") or path in PUBLIC_PATHS or path.startswith("/docs"):
        return await call_next(request)
    
    # Check session cookie
    token = request.cookies.get(SESSION_COOKIE)
    if not token or not verify_session_token(token):
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return await call_next(request)

# Mount all routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(scraper.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(applications.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
