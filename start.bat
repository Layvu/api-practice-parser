@echo off
echo Starting FastAPI server...
start /B python -m uvicorn main:app --reload > server.log 2>&1
timeout /t 3 > nul
start notifications.html
