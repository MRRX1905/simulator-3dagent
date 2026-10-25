# AI City Test Suite Runner
Write-Host "Running AI City Backend Test Suite (pytest)..." -ForegroundColor Cyan

$backendDir = "C:\AI_CITY\backend"
$pythonExe = "$backendDir\.venv\Scripts\python.exe"

$env:PYTHONPATH = $backendDir
& $pythonExe -m pytest "$backendDir\tests" -v
