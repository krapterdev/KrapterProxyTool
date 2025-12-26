from passlib.context import CryptContext
from database import get_db_connection
import psycopg2

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(email, password, proxy_limit=15, is_admin=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = get_password_hash(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, proxy_limit, is_admin) VALUES (%s, %s, %s, %s)", 
            (email, hashed_password, proxy_limit, is_admin)
        )
        conn.commit()
        print(f"User '{email}' created successfully.")
    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"User '{email}' already exists.")
    except Exception as e:
        conn.rollback()
        print(f"Error creating user: {e}")
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    # Use RealDictCursor to access columns by name
    from psycopg2.extras import RealDictCursor
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    return user

# Create default admin user if not exists
def init_auth():
    create_user("krapter.dev@gmail.com", "Chikki!@#1998", proxy_limit=1000, is_admin=True)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import redis_client

# Auth Config
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokens = {} # In-memory token store {token: email}

def get_current_user_obj(token: str = Depends(oauth2_scheme)):
    email = tokens.get(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = redis_client.get_user_by_email(email)
    if not user:
         raise HTTPException(status_code=401, detail="User not found")
    return user

if __name__ == "__main__":
    init_auth()
