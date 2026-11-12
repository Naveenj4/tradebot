# TradeBot 1.0 - One-Click Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   ⚡ TradeBot 1.0 - NSE Options Algorithmic System       " -ForegroundColor Yellow
Write-Host "   Broker: Angel One SmartAPI | Interface: React 19 UI   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$VENV_PYTHON = "D:\tradebot_venv\Scripts\python.exe"

if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "[ERROR] Virtual environment python not found at $VENV_PYTHON" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n[1/2] Verifying database and tables..." -ForegroundColor Gray
& $VENV_PYTHON -c "import asyncio; from src.storage.session import init_db; asyncio.run(init_db()); print('Database verified.')"

Write-Host "`n[2/2] Starting TradeBot Backend & React Dashboard on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor Gray

& $VENV_PYTHON src/main.py

