from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.routes.auth import get_current_user
from app.database import get_db
import psycopg2.extras

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- Owner Dashboard ---
@router.get("/owner/users", response_class=HTMLResponse)
def owner_users(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    
    return templates.TemplateResponse("dashboard/owner_users.html", {
        "request": request,
        "user": user,
        "users": users,
        "session": request.session
    }) 

# --- HR View Team ---
@router.get("/hr/team")
def hr_team(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT name, email FROM users WHERE role = 'employee'")
    employees = cursor.fetchall()
    cursor.close()
    db.close()
    return templates.TemplateResponse("dashboard/hr.html", {"request": request, "user": user, "employees": employees})

@router.get("/hr_notifications", response_class=HTMLResponse)
def notifications(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["role"] != "hr":
        return RedirectResponse("/login")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Only fetch moods of employees under this HR
    cursor.execute("""
        SELECT u.name AS employee, m.detected_emotion, m.created_at
        FROM moods m
        JOIN users u ON m.user_id = u.id
        WHERE m.detected_emotion = 'stressed' AND u.hr_id = %s
        ORDER BY m.created_at DESC
    """, (user["id"],))
    results = cursor.fetchall()

    # Convert into notifications format
    notifications = []
    for row in results:
        notifications.append({
            "employee": row["employee"],
            "message": "has shown signs of stress",
            "created_at": row["created_at"]
        })

    cursor.close()
    db.close()

    return templates.TemplateResponse("dashboard/hr_notifications.html", {
        "request": request,
        "user": user,
        "notifications": notifications,
        "session": request.session
    })


@router.get("/owner/teams", response_class=HTMLResponse)
def owner_hr_groups(request: Request, user: dict = Depends(get_current_user)):
    if user["role"] != "owner":
        return RedirectResponse("/login")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get all HRs
    cursor.execute("SELECT id, name FROM users WHERE role = 'hr'")
    hrs = cursor.fetchall()

    # For each HR, fetch their employees
    hr_groups = []
    for hr in hrs:
        cursor.execute("SELECT name, email FROM users WHERE hr_id = %s", (hr["id"],))
        employees = cursor.fetchall()
        hr_groups.append({
            "hr": hr["name"],
            "employees": employees
        })
 
    cursor.close()
    db.close()

    return templates.TemplateResponse("dashboard/owner_teams.html", {
        "request": request,
        "user": user,
        "hr_groups": hr_groups,
        "session": request.session
    })
