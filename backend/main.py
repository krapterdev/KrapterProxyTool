from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from router import router
from auth import authenticate_user, create_access_token, oauth2_scheme, get_current_user_obj, init_auth, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
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

@app.on_event("startup")
async def startup_event():
    # Initialize DB and Auth
    print("Starting up... Initializing Auth...")
    try:
        init_auth()
    except Exception as e:
        print(f"Error during startup auth init: {e}")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm has 'username' field, we use it for email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Include API Router
app.include_router(router)
