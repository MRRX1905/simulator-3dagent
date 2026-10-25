# AI CITY — Backend Startup Script (PowerShell)
# Usage: Right-click -> Run with PowerShell, or: .\start_backend.ps1

$Host.UI.RawUI.WindowTitle = "AI CITY Backend"
$BackendDir = "C:\AI_CITY\backend"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║      AI CITY — Backend Server        ║" -ForegroundColor Cyan
Write-Host "  ║  FastAPI + SQLite + LLM Integration  ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Set-Location $BackendDir

# Create venv if missing
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate venv
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
& ".venv\Scripts\Activate.ps1"

# Install deps
Write-Host "[INFO] Installing dependencies..." -ForegroundColor Green
pip install -q -r requirements.txt

Write-Host ""
Write-Host "[INFO] Backend URL : http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "[INFO] API Docs    : http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] 3D Frontend : Open C:\AI_CITY\game_assets\index.html in Chrome" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Starting server... (Ctrl+C to stop)" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
