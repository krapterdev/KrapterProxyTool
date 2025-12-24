from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os

app = FastAPI()

# Configuration
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/proxylist", response_class=HTMLResponse)
async def read_proxylist(request: Request):
    return templates.TemplateResponse("proxylist.html", {"request": request})

if __name__ == "__main__":
    # This allows running 'python app.py' directly if needed
    uvicorn.run(app, host="0.0.0.0", port=8080)
