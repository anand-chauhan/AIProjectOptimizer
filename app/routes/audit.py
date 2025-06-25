from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.routes.auth import get_current_user
from app.database import get_db
import psycopg2.extras

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/audit", response_class=RedirectResponse)
def audit_logs(request: Request, user: dict = Depends(get_current_user)):
    if not user or user["role"] != "owner":
        return RedirectResponse("/login")
 
    db = get_db() 
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT users.name, moods.mood_source, moods.detected_emotion, moods.created_at
        FROM moods
        JOIN users ON moods.user_id = users.id
        ORDER BY moods.created_at DESC
    """)
    logs = cursor.fetchall()
    cursor.close()
    db.close()

    return templates.TemplateResponse("dashboard/audit.html", {
        "request": request,
        "user": user,
        "logs": logs,
        "session": request.session
    })
