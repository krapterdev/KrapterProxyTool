from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="ProxyHub Frontend")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    backend_url = os.getenv("BACKEND_URL", "http://localhost:2223")
    return templates.TemplateResponse("dashboard.html", {"request": request, "BACKEND_URL": backend_url})

@app.get("/proxylist", response_class=HTMLResponse)
async def read_proxylist(request: Request):
    backend_url = os.getenv("BACKEND_URL", "http://localhost:2223")
    return templates.TemplateResponse("proxylist.html", {"request": request, "BACKEND_URL": backend_url})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    backend_url = os.getenv("BACKEND_URL", "http://localhost:2223")
    return templates.TemplateResponse("login.html", {"request": request, "BACKEND_URL": backend_url})



@app.get("/proxies/all")
async def get_proxies():
    # This seems to be a frontend proxy to backend? Or just unused?
    # The frontend fetches directly from BACKEND_URL (port 8000).
    # This app.py is running on port 3000 (usually) serving HTML.
    pass
