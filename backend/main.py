from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from router import router
from auth import authenticate_user
import secrets

app = FastAPI(title="Krapter Proxy Tool - Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokens = {} # In-memory token store {token: username}

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = tokens.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm has 'username' field, we use it for email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = secrets.token_hex(16)
    # Store full user info or just email? Let's store email and fetch user on request to get latest limit
    tokens[token] = user["email"]
    return {"access_token": token, "token_type": "bearer"}

# Include API Router (Protected)
# We pass get_current_user as a dependency to the router so endpoints can access the user
# Note: The router functions need to accept 'current_user' argument
from database import redis_client

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

app.include_router(router, dependencies=[Depends(get_current_user_obj)])
