# AI City Health Check Script
Write-Host "Checking AI City Backend Services..." -ForegroundColor Cyan

try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 3
    Write-Host "[OK] Health Check:" ($health | ConvertTo-Json -Compress) -ForegroundColor Green

    $world = Invoke-RestMethod -Uri "http://127.0.0.1:8000/world" -Method Get -TimeoutSec 3
    Write-Host "[OK] World State:" ($world | ConvertTo-Json -Compress) -ForegroundColor Green

    $agents = Invoke-RestMethod -Uri "http://127.0.0.1:8000/agents" -Method Get -TimeoutSec 3
    Write-Host "[OK] Active Agents Count:" $agents.Count -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Could not connect to AI City backend at http://127.0.0.1:8000. Is the server running?" -ForegroundColor Red
}
