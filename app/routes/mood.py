import os
import logging
from fastapi import APIRouter, Form, Request, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ai_mood_analysis import analyze_text_mood
from app.database import get_db
from app.routes.auth import get_current_user
from app.services.facial_detector import detect_emotion_from_image
from app.services.voice_detector import detect_mood_from_audio
from app.services.task_assigner import assign_task_based_on_mood

router = APIRouter()
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger("zidio")
logging.basicConfig(level=logging.INFO)

# --------------------------- TEXT MOOD ---------------------------

@router.get("/mood", response_class=HTMLResponse)
async def get_mood_form(request: Request):
    user = get_current_user(request) 
    return templates.TemplateResponse("mood/text.html", {
        "request": request,
        "user": user
    })

@router.post("/mood")
async def submit_mood(request: Request, mood_text: str = Form(...)):
    user = request.session.get("user")
    if not user or not user.get("id"):
        logger.error("❌ No user found in session or missing 'id'. Redirecting to login.")
        return RedirectResponse("/login", status_code=302)

    user_id = user["id"]

    analysis = analyze_text_mood(mood_text)
    emotion = analysis["emotion"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO moods (user_id, mood_text, mood_source, detected_emotion) VALUES (%s, %s, %s, %s)",
        (user["id"], mood_text, "text", emotion)
    )
    db.commit()
    cursor.close()
    db.close()

    try:
        if not user or "id" not in user:
            raise ValueError("❌ Invalid session user before assigning task")

        task_info = assign_task_based_on_mood(user_id, emotion)
        body = f"Task: {task_info['task_title']}\nPriority: {task_info['priority']}\nBased on your mood: {emotion}"
    except Exception as e:
        logger.error("Text task assignment failed", exc_info=True)
        task_info = None
        body = f"Detected mood: {emotion}. Task assignment failed."

    return templates.TemplateResponse("mood/text.html", {
        "request": request,
        "user": user,
        "result": analysis,
        "mood_text": mood_text,
        "task_info": task_info,
        "message": body,
        "session": request.session
    })

# --------------------------- FACIAL MOOD ---------------------------

@router.get("/mood/facial", response_class=HTMLResponse)
async def get_facial_form(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("mood/facial.html", {
        "request": request,
        "user": user
    })

@router.post("/mood/facial")
async def post_facial_mood(request: Request, file: UploadFile = File(...)):
    user = request.session.get("user")
    if not user or not user.get("id"):
        logger.error("❌ No user found in session or missing 'id'. Redirecting to login.")
        return RedirectResponse("/login", status_code=302)

    user_id = user["id"]

    # ✅ Declare early so it always exists
    image_path = None

    try:
        contents = await file.read()
        os.makedirs("temp_faces", exist_ok=True)
        image_path = f"temp_faces/{file.filename}"
        with open(image_path, "wb") as f:
            f.write(contents)

        emotion = detect_emotion_from_image(image_path)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO moods (user_id, mood_text, mood_source, detected_emotion) VALUES (%s, %s, %s, %s)",
            (user["id"], "Facial submission", "facial", emotion)
        )
        db.commit()
        cursor.close()
        db.close()

        try:
            if not user or "id" not in user:
                raise ValueError("❌ Invalid session user before assigning task")

            task_info = assign_task_based_on_mood(user_id, emotion)
            body = f"Task: {task_info['task_title']}\nPriority: {task_info['priority']}\nBased on your mood: {emotion}"
        except Exception as e:
            logger.error("Facial task assignment failed", exc_info=True)
            task_info = None
            body = f"Detected mood: {emotion}. Task assignment failed."
    
    except Exception as e:
        logger.error("Facial mood detection failed", exc_info=True)
        emotion = "unknown"
        task_info = None
        body = f"Facial detection failed: {str(e)}"

    finally:
        # ✅ Safe cleanup check
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    return templates.TemplateResponse("mood/facial.html", {
        "request": request,
        "user": user,
        "emotion": emotion,
        "task_info": task_info,
        "message": body,
        "session": request.session
    })

# --------------------------- VOICE MOOD ---------------------------

@router.get("/mood/voice", response_class=HTMLResponse)
async def get_voice_form(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("mood/voice.html", {
        "request": request,
        "user": user
    })
 
@router.post("/mood/voice")
async def post_voice_mood(request: Request, file: UploadFile = File(...)):
    user = request.session.get("user")
    if not user or not user.get("id"):
        logger.error("❌ No user found in session or missing 'id'. Redirecting to login.")
        return RedirectResponse("/login", status_code=302)

    user_id = user["id"]

    try:
        analysis = detect_mood_from_audio(file)
        emotion = analysis["emotion"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO moods (user_id, mood_text, mood_source, detected_emotion) VALUES (%s, %s, %s, %s)",
            (user["id"], analysis["transcript"], "voice", emotion)
        )
        db.commit()
        cursor.close()
        db.close()

        try:
            if not user or "id" not in user:
                raise ValueError("❌ Invalid session user before assigning task")

            task_info = assign_task_based_on_mood(user_id, emotion)
            body = f"Task: {task_info['task_title']}\nPriority: {task_info['priority']}\nBased on your mood: {emotion}"
        except Exception as e:
            logger.error("Voice task assignment failed", exc_info=True)
            task_info = None
            body = f"Detected mood: {emotion}. Task assignment failed."
        
    except Exception as e:
        logger.error("Voice mood detection failed", exc_info=True)
        analysis = {"transcript": "", "emotion": "unknown"}
        task_info = None
        body = f"Voice detection failed: {str(e)}"

    return templates.TemplateResponse("mood/voice.html", {
        "request": request,
        "user": user,
        "result": analysis,
        "task_info": task_info,
        "message": body,
        "session": request.session
    })
