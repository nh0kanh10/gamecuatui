@echo off
chcp 65001 >nul
title 🎮 Cultivation Simulator - Quick Start

:: ============================================
:: ⚡ ULTRA QUICK START - MINIMAL OUTPUT
:: ============================================

@echo off
set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
cd /d "%GAME_DIR%"

:: Quick checks
python --version >nul 2>&1 || (echo Python not found! && pause && exit /b 1)

:: Clean ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Start backend
start "Backend" cmd /k "cd /d "%GAME_DIR%" && python -u server.py"

:: Wait and start frontend
timeout /t 3 >nul
if exist "cultivation-ui\node_modules" (
    set "UI_FULL_PATH=%GAME_DIR%\cultivation-ui"
    if exist "%UI_FULL_PATH%\package.json" (
        start "Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && if exist package.json (npm run dev) else (echo ❌ Error: package.json not found && pause)"
        timeout /t 2 >nul
        start http://localhost:5173
    ) else (
        echo ⚠️  Frontend: package.json not found
    )
)

echo.
echo ✅ Game started! Check the windows that opened.
echo.
pause

