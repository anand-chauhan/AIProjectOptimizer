import random
import logging
from fastapi.requests import Request
from app.database import get_db
import psycopg2.extras
from app.services.notification import notify_hr_of_stress

logger = logging.getLogger("zidio")

AI_ASSIGNED_BY_ID = 1

MOOD_TASK_MAP = {
    "happy": ("Work on high-priority task", "Proceed with a critical project task.", "High"),
    "motivated": ("Work on high-priority task", "Proceed with a critical project task.", "High"),
    "neutral": ("Continue with standard tasks", "Keep working on your assigned tasks.", "Medium"),
    "calm": ("Continue with standard tasks", "Keep working on your assigned tasks.", "Medium"),
    "stressed": ("Take a short break or review light tasks", "Low pressure work assigned for stress recovery.", "Low"),
    "sad": ("Focus on simple tasks or take a break", "Assign easy or relaxing work.", "Low"),
    "angry": ("De-escalate with solo or quiet task", "Assigned independent or non-pressuring tasks.", "Low"),
    "fear": ("Light analysis or documentation work", "Assign calm-focused work like reading or documenting.", "Low"),
    "surprise": ("Review recent tasks and reflect", "Assigned reflection task to ground your focus.", "Medium"),
    "disgust": ("Solo task with minimal social input", "Assign work requiring minimal collaboration.", "Low"),
    "bored": ("Try a creative mini-task or ideation", "Boost engagement with creative, optional task.", "Medium")
}

def assign_task_based_on_mood(user_id: int, emotion: str) -> dict:
    if not user_id:
        raise ValueError("❌ Cannot assign task — user_id is missing.")

    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    task_title, task_description, priority = MOOD_TASK_MAP.get(
        emotion.lower(), 
        ("Complete a standard task", "Maintain your workflow with regular task.", "Medium")
    )

    logger.info(f"Assigning task to user {user_id}: {task_title} ({priority})")

    try:
        cursor.execute(
            "INSERT INTO tasks (user_id, assigned_to, task_title, task_description, priority, assigned_by) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, user_id, task_title, task_description, priority, AI_ASSIGNED_BY_ID)
        )

        cursor.execute(
            "INSERT INTO mood_history (user_id, mood, detection_method) VALUES (%s, %s, %s)",
            (user_id, emotion, "facial")
        )

        cursor.execute(
            "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
            (user_id, f"Mood: {emotion} → Task: {task_title} [{priority}]")
        )

        if emotion.lower() == "stressed":
            cursor.execute("SELECT hr_id FROM users WHERE id = %s", (user_id,))
            hr = cursor.fetchone()
            if hr and hr["hr_id"]:
                notify_hr_of_stress(
                    user_id=user_id,
                    hr_id=hr["hr_id"],
                    message=f"⚠️ Employee ID {user_id} has reported being stressed. Assigning stress recovery task."
                )

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Task insert failed for user {user_id}: {e}")
        raise e
    finally:
        cursor.close()
        db.close()

    return {
        "task_title": task_title,
        "description": task_description,
        "priority": priority
    }
