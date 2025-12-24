@echo off
title Krapter Setup
echo Installing dependencies...

echo.
echo [Backend]
python -m pip install -r backend/requirements.txt

echo.
echo [Worker]
python -m pip install -r worker/requirements.txt

echo.
echo [Frontend]
python -m pip install -r frontend/requirements.txt

echo.
echo Done! You can now run 'python start.py'
pause
