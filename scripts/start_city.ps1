# AI City Startup Script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Starting AI City Backend Core" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$backendDir = "C:\AI_CITY\backend"
$pythonExe = "$backendDir\.venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Virtual environment not found at $pythonExe! Please run setup first." -ForegroundColor Red
    exit 1
}

$env:PYTHONPATH = $backendDir

Write-Host "Launching FastAPI Uvicorn on http://127.0.0.1:8000..." -ForegroundColor Green
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
