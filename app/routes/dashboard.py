from fastapi import Depends, Request
from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.routes.auth import get_current_user
from app.services.notification import notify_hr_of_stress
import psycopg2.extras

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/hr", response_class=HTMLResponse)
async def hr_dashboard(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "hr": 
        return RedirectResponse("/login")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # 💡 Only fetch employees where this HR is their hr_id
    cursor.execute("""
        SELECT u.id, u.name, u.email, MAX(m.detected_emotion) AS latest_mood
        FROM users u
        LEFT JOIN moods m ON u.id = m.user_id
        WHERE u.role = 'employee' AND u.hr_id = %s
        GROUP BY u.id
    """, (user["id"],))
    employees = cursor.fetchall()

    cursor.execute("""
        SELECT t.*, u.name AS employee_name FROM tasks t
        JOIN users u ON u.id = t.assigned_to
        WHERE u.hr_id = %s
        ORDER BY t.created_at DESC LIMIT 20
    """, (user["id"],))
    tasks = cursor.fetchall()
 
    # 🧠 Stressed users under this HR only
    cursor.execute("""
        SELECT user_id, COUNT(*) as stress_count, u.name
        FROM moods m
        JOIN users u ON m.user_id = u.id
        WHERE detected_emotion = 'stressed' AND u.hr_id = %s
        GROUP BY user_id
        HAVING stress_count >= 2
    """, (user["id"],))
    stressed_users = cursor.fetchall()

    if stressed_users:
        for s in stressed_users:
            message = f"⚠️ {s['name']} is showing signs of stress ({s['stress_count']} times)"
            notify_hr_of_stress(user_id=s["user_id"], hr_id=user["id"], message=message)

    cursor.close()
    db.close()

    return templates.TemplateResponse("hr_dashboard.html", {
        "request": request,
        "employees": employees,
        "tasks": tasks,
        "stressed": stressed_users,
        "session": request.session
    })

@router.get("/weekly-moods", response_class=HTMLResponse)
async def weekly_mood_stats(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    role = user.get("role")
    user_id = user.get("id")

    if role == "employee":
        # 👤 Show only employee’s own mood
        cursor.execute("""
            SELECT mood, COUNT(*) as count
            FROM mood_history
            WHERE user_id = %s AND timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY mood
        """, (user_id,))
    
    elif role == "hr":
        # 👥 Show moods of all employees under this HR
        cursor.execute("""
            SELECT mood, COUNT(*) as count
            FROM mood_history mh
            JOIN users u ON mh.user_id = u.id
            WHERE u.hr_id = %s AND timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY mood
        """, (user_id,))

    else:
        # 🧠 Owner show all users
        cursor.execute("""
            SELECT mood, COUNT(*) as count
            FROM mood_history
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY mood
        """)

    stats = cursor.fetchall()
    cursor.close()
    db.close()

    return templates.TemplateResponse("analytics/weekly_moods.html", {
        "request": request,
        "stats": stats,
        "user": user,
        "session": request.session
    })

@router.get("/dashboard")
def dashboard(request: Request, user: dict = Depends(get_current_user)):
    role = user["role"]

    if role == "employee":
        return templates.TemplateResponse("dashboard/employee.html", {"request": request, "user": user})
    elif role == "hr":
        return templates.TemplateResponse("dashboard/hr.html", {"request": request, "user": user})
    elif role == "owner":
        return templates.TemplateResponse("dashboard/owner.html", {"request": request, "user": user})
    else:
        return RedirectResponse("/", status_code=302)
    
@router.get("/dashboard/employee", response_class=HTMLResponse)
def employee_dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/employee.html", {"request": request, "user": user})

@router.get("/dashboard/hr", response_class=HTMLResponse)
def hr_dashboard(request: Request, user: dict = Depends(get_current_user)):
    # you already have HR logic in place here
    ...

@router.get("/dashboard/owner", response_class=HTMLResponse)
def owner_dashboard(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return templates.TemplateResponse("dashboard/owner.html", {"request": request, "user": user, "users": users})

@router.get("/hr/filter", response_class=HTMLResponse)
def hr_filter_moods(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["role"] != "hr":
        return RedirectResponse("/login")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT u.name, m.detected_emotion, m.created_at
        FROM moods m
        JOIN users u ON m.user_id = u.id
        WHERE u.hr_id = %s
        ORDER BY m.created_at DESC
    """, (user["id"],))

    moods = cursor.fetchall()
    cursor.close()
    db.close()

    return templates.TemplateResponse("dashboard/hr_filter.html", {
        "request": request,
        "user": user,
        "moods": moods,
        "session": request.session
    })
