@echo off
rem =====================================================================
rem SERA JULIUS PLATFORM — ONE-CLICK WINDOWS DEPLOYMENT SCRIPT
rem =====================================================================

echo ---------------------------------------------------------------------
echo  [SERA DEPLOY] Initializing SERA Julius Platform Deployment...
echo ---------------------------------------------------------------------

rem 1. Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [SERA DEPLOY] Local server mode: Launching FastAPI + Vite Dev Servers...
    goto LOCAL_MODE
)

echo [SERA DEPLOY] Docker detected. Launching Docker Microservices...
docker compose up -d --build
goto DONE

:LOCAL_MODE
echo [SERA DEPLOY] Starting Backend API on http://localhost:8000...
start /b python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

echo [SERA DEPLOY] Starting Frontend Web App on http://localhost:5173...
cd frontend
npm run dev

:DONE
echo ---------------------------------------------------------------------
echo  ✅ SERA JULIUS PLATFORM IS LIVE & DEPLOYED!
echo ---------------------------------------------------------------------
