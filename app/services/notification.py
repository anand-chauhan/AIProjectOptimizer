from app.database import get_db

def notify_hr_of_stress(user_id: int, hr_id: int, message: str):
    """
    Insert an in-app notification into the notifications table for HR
    when their assigned employee is stressed.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO notifications (user_id, hr_id, message)
            VALUES (%s, %s, %s)
        """, (user_id, hr_id, message))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[NOTIFICATION ERROR] Failed to notify HR: {e}")
    finally:
        cursor.close()
        db.close()
  