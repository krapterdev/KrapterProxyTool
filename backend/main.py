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
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = secrets.token_hex(16)
    tokens[token] = user["username"]
    return {"access_token": token, "token_type": "bearer"}

# Include API Router (Protected)
# We exclude /api/proxies/external from protection if we want public access, 
# but for now let's protect everything. The user can use the token.
app.include_router(router, dependencies=[Depends(get_current_user)])
