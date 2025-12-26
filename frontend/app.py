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
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/proxylist", response_class=HTMLResponse)
async def read_proxylist(request: Request):
    return templates.TemplateResponse("proxylist.html", {"request": request})
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/proxies/all")
async def get_proxies():
    # This seems to be a frontend proxy to backend? Or just unused?
    # The frontend fetches directly from BACKEND_URL (port 8000).
    # This app.py is running on port 3000 (usually) serving HTML.
    pass
