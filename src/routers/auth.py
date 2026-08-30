from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.core.auth import create_session_token, verify_password, SESSION_COOKIE

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse(request=request, name="auth/login.html", context={"request": request, "error": error})

@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    if verify_password(password):
        token = create_session_token()
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            httponly=True,
            max_age=60 * 60 * 24 * 7,
            samesite="lax"
        )
        return response
    return templates.TemplateResponse(request=request, name="auth/login.html", context={
        "request": request,
        "error": "Incorrect password. Try again."
    })

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE)
    return response
