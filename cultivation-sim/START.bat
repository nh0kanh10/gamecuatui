@echo off
chcp 65001 >nul
title Cultivation Simulator
color 0B

echo.
echo ========================================
echo    🌟 CULTIVATION SIMULATOR 🌟
echo ========================================
echo.

:: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo ✅ Python OK

:: Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js
    pause
    exit /b 1
)
echo ✅ Node.js OK

:: Check dependencies
echo [3/5] Checking dependencies...
if not exist "cultivation-ui\node_modules" (
    echo ⏳ Installing UI dependencies...
    cd cultivation-ui
    call npm install
    cd ..
)
echo ✅ Dependencies OK

:: Kill old processes
echo [4/5] Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5174') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo ✅ Ports cleaned

:: Start servers
echo [5/5] Starting servers...
echo.
echo 📍 Backend: http://localhost:8001
echo 📍 Frontend: http://localhost:5173
echo.

:: Start backend
echo ⏳ Starting backend server...
start "Cultivation Server" cmd /k "cd /d %~dp0 && python server.py"
timeout /t 5 >nul

:: Start frontend
echo ⏳ Starting frontend UI...
start "Cultivation UI" cmd /k "cd /d %~dp0cultivation-ui && npm run dev"
timeout /t 8 >nul

:: Open browser
echo ⏳ Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo    ✅ GAME STARTED!
echo ========================================
echo.
echo 💡 Two windows opened:
echo    1. Backend Server (Python - Port 8001)
echo    2. Frontend UI (Vite - Port 5173)
echo.
echo 🎮 Game should open in browser automatically!
echo.
echo ⚠️  Keep both windows open while playing!
echo 🛑 Close this window anytime to stop.
echo.
pause
