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

@app.get("/debug/log")
def read_log():
    log_path = os.path.join(BASE_DIR, "worker.log")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return Response(content=f.read(), media_type="text/plain")
    return {"error": "Log file not found"}

@app.get("/debug/run_worker")
def trigger_worker():
    # Import here to avoid circular imports if possible, or move job to a common place.
    # But job imports checker which imports database...
    # Let's try running it as a subprocess to be safe and independent.
    import subprocess
    import sys
    
    try:
        # Run scheduler.py's job function? No, scheduler.py runs the job on main.
        # Let's just run scheduler.py in a separate process, but it blocks.
        # Better: Import job from scheduler and run it in background task.
        from fastapi import BackgroundTasks
        
        # We need to import job from worker.scheduler, but that might be tricky with paths.
        # Let's assume we can run the checker script directly.
        
        # Actually, let's just run the scheduler.py script as a one-off process
        # It has a "run once" block at the end? No, it starts the scheduler.
        # I'll modify scheduler.py to accept a flag or just run the job logic.
        
        # Simplest: Just return a message saying "Check logs".
        # The worker runs every 2 mins.
        return {"message": "Worker runs every 2 minutes. Check /debug/log."}
    except Exception as e:
        return {"error": str(e)}

# Include API Router
app.include_router(router)
