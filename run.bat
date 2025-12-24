@echo off
title Krapter Proxy Tool Launcher

echo ===================================================
echo 🚀 Krapter Proxy Tool - Hybrid Launcher
echo ===================================================

echo.
echo [1/4] Starting Redis (Docker)...
docker-compose up -d redis
if %errorlevel% neq 0 (
    echo Failed to start Redis. Make sure Docker Desktop is running.
    pause
    exit /b
)

echo.
echo [2/4] Installing Python Dependencies...
python -m pip install -r backend/requirements.txt
python -m pip install -r worker/requirements.txt
python -m pip install -r frontend/requirements.txt

echo.
echo [3/4] Starting Services...

:: Start Backend
echo Starting Backend (Port 8000)...
start "Krapter Backend" cmd /k "set REDIS_PORT=6380 && cd backend && uvicorn main:app --reload --port 8000"

:: Start Worker
echo Starting Worker...
start "Krapter Worker" cmd /k "set REDIS_PORT=6380 && cd worker && python scheduler.py"

:: Start Frontend
echo Starting Frontend (Port 8080)...
start "Krapter Frontend" cmd /k "set BACKEND_URL=http://localhost:8000 && cd frontend && python app.py"

echo.
echo ===================================================
echo ✅ All systems go!
echo Dashboard: http://localhost:8080
echo API Docs:  http://localhost:8000/docs
echo ===================================================
pause
