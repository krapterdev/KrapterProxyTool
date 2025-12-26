from passlib.context import CryptContext
from database import get_db_connection
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(username, password):
    conn = get_db_connection()
    try:
        hashed_password = get_password_hash(password)
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print(f"User '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    return user

# Create default admin user if not exists
def init_auth():
    create_user("admin", "admin123")

if __name__ == "__main__":
    init_auth()
