@echo off
title Clean and Safe India - Real-Time Smart Civic Platform
cd /d "%~dp0"
echo ===================================================================
echo   Clean ^& Safe India - Real-Time Backend ^& Smart Civic Platform
echo   Features: Persistent SQLite DB, REST API, Live SSE Event Hub
echo ===================================================================
echo.
echo Starting Real-Time Backend Server on http://localhost:8000 ...
start http://localhost:8000
python server.py
pause
