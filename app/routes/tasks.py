from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.routes.auth import get_current_user
from app.database import get_db
import psycopg2.extras

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tasks", response_class=RedirectResponse)
def employee_tasks(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["role"] != "employee":
        return RedirectResponse("/login")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT task_title, task_description, priority, status, created_at
        FROM tasks
        WHERE assigned_to = %s
        ORDER BY created_at DESC
    """, (user["id"],))

    tasks = cursor.fetchall()
    cursor.close()
    db.close()

    return templates.TemplateResponse("dashboard/tasks.html", {
        "request": request, 
        "user": user,
        "tasks": tasks,
        "session": request.session
    })
 