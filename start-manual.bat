@echo off
chcp 65001 >nul
echo ========================================
echo   Portfolio Backtest - Manual Start
echo ========================================
echo.
echo Please start services manually in separate terminals:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   py run.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Or use these commands directly:
echo.
echo Backend:  start cmd /k "cd backend && py run.py"
echo Frontend: start cmd /k "cd frontend && npm run dev"
echo.
echo ========================================
echo.

choice /C YN /M "Do you want to start both services now"
if errorlevel 2 goto :end
if errorlevel 1 goto :start

:start
echo.
echo Starting backend service...
start "Backend Service" cmd /k "cd /d "%~dp0backend" && py run.py"

echo Starting frontend service...
start "Frontend Service" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Services starting in separate windows...
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
timeout /t 3 >nul

:end
