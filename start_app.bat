@echo off
echo ===================================================
echo       Starting AI Chat System
echo ===================================================

echo.
echo [1/2] Launching Backend Server...
start "Backend Server (FastAPI)" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo.
echo [2/2] Launching Frontend Server...
start "Frontend Server (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo       System Started!
echo       Frontend: http://localhost:5173
echo       Backend:  http://localhost:8000
echo ===================================================
echo.
echo You can minimize this window, but do not close the popped-up server windows.
echo.
pause
