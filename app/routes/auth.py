from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from app.services.auth_service import create_user, validate_user
from app.database import get_db
import psycopg2.extras

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request):
    return request.session.get("user")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    session = request.session
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": get_current_user(request),  
        "session": request.session
    })

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT id, name FROM users WHERE role = 'hr'")
    hr_list = cursor.fetchall()
    cursor.close()
    db.close()
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": None,
        "hr_list": hr_list,
        "session": request.session
    })

@router.post("/register")
async def register_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...),
    hr_id: int = Form(None),
    role: str = Form("employee")
):
    if password != confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match."})
    try:
        create_user(name, email, password, role, hr_id)
    except ValueError as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = validate_user(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})

    request.session["user"] = user

    # Redirect based on role
    role = user["role"]
    if role == "employee":
        return RedirectResponse("/dashboard", status_code=302)
    elif role == "hr":
        return RedirectResponse("/dashboard", status_code=302)
    elif role == "owner":
        return RedirectResponse("/dashboard", status_code=302)
    else:
        return RedirectResponse("/", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
 
    role = user["role"]
    dashboard_template = f"dashboard/{role}.html"  # e.g. dashboard/hr.html

    return templates.TemplateResponse(dashboard_template, {
        "request": request,
        "user": user,
        "session": request.session 
    })

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
