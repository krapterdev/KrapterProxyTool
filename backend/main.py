from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router

app = FastAPI(title="Krapter Proxy Tool - Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)
