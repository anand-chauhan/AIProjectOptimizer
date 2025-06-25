import bcrypt
from app.database import get_db
from psycopg2 import IntegrityError
import psycopg2.extras

def create_user(name: str, email: str, password: str, role: str, hr_id: int = None):
    db = get_db()
    cursor = db.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        if role == "employee":
            cursor.execute(
                "INSERT INTO users (name, email, password, role, hr_id) VALUES (%s, %s, %s, %s, %s)",
                (name, email, hashed, role, hr_id)
            )
        else:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed, role)
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Email already registered.")
    finally:
        cursor.close() 
        db.close()

def validate_user(email, password):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT id, name, password, role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return {"id": user["id"], "name": user["name"], "role": user["role"]}

    return None
 