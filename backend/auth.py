from passlib.context import CryptContext
from database import get_db_connection, PostgresClient
import psycopg2
import os
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

# Initialize PostgresClient for auth checks
redis_client = PostgresClient() 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key") # IMPORTANT: Change this in production!
ALGORITHM = "HS256"

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

# Auth Config
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user_obj(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = redis_client.get_user_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user

async def get_api_key_user(
    api_key: str = Security(api_key_header)
):
    if not api_key:
        return None
        
    user = redis_client.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return user

async def get_dual_auth_user(
    api_key: str = Security(api_key_header),
    token: str = Depends(oauth2_scheme)
):
    # 1. Try API Key
    if api_key:
        user = redis_client.get_user_by_api_key(api_key)
        if user:
            return user
    
    # 2. Try Bearer Token
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email:
                user = redis_client.get_user_by_email(email)
                if user:
                    return user
        except JWTError:
            pass
            
    # 3. Fail
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated (Token or API Key required)",
        headers={"WWW-Authenticate": "Bearer"},
    )

if __name__ == "__main__":
    init_auth()
