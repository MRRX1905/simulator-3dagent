@echo off
title AI CITY — 3D Frontend
color 0B
echo.
echo  Starting AI CITY 3D Frontend Server...
echo  ========================================
echo  URL: http://127.0.0.1:3000
echo  Press Ctrl+C to stop
echo.

REM Serve game_assets on port 3000 (backend must run on 8000 separately)
python -m http.server 3000 --bind 127.0.0.1 --directory "C:\AI_CITY\game_assets"
pause
