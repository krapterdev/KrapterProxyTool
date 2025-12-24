from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from router import router
import os

app = FastAPI(title="Krapter Proxy Tool")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates Configuration
# backend/main.py -> parent -> frontend -> templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
print(f"DEBUG: TEMPLATES_DIR = {TEMPLATES_DIR}")

if not os.path.exists(TEMPLATES_DIR):
    print("⚠️ WARNING: TEMPLATES_DIR does not exist!")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Frontend Routes (Defined BEFORE router to ensure priority)
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    print("DEBUG: Accessing Dashboard")
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/proxylist", response_class=HTMLResponse)
async def read_proxylist(request: Request):
    return templates.TemplateResponse("proxylist.html", {"request": request})

@app.get("/health")
def health_check():
    return {"status": "ok", "templates_dir": TEMPLATES_DIR, "exists": os.path.exists(TEMPLATES_DIR)}

@app.get("/favicon.ico")
async def favicon():
    return Response(content=b"", media_type="image/x-icon")

# Include API Router
app.include_router(router)
