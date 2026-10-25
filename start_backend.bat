@echo off
title AI CITY — Backend Server
color 0A
echo.
echo  ██████╗ ██╗      ██████╗██╗████████╗██╗   ██╗
echo  ██╔══██╗██║     ██╔════╝██║╚══██╔══╝╚██╗ ██╔╝
echo  ██████╔╝██║     ██║     ██║   ██║    ╚████╔╝ 
echo  ██╔══██╗██║     ██║     ██║   ██║     ╚██╔╝  
echo  ██║  ██║███████╗╚██████╗██║   ██║      ██║   
echo  ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝   ╚═╝      ╚═╝  
echo.
echo  AI CITY Backend — FastAPI + SQLite + LLM
echo  ============================================
echo.

cd /d C:\AI_CITY\backend

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Creating...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Python not found. Install Python 3.10+ from python.org
        pause
        exit /b 1
    )
)

REM Activate venv and install deps
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Installing/updating dependencies...
pip install -q -r requirements.txt

echo.
echo [INFO] Starting FastAPI server on http://127.0.0.1:8000
echo [INFO] API Docs: http://127.0.0.1:8000/docs
echo [INFO] Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
