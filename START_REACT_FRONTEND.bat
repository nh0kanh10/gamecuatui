@echo off
chcp 65001 >nul
title Cultivation Simulator - React Frontend

:: ============================================
:: 🎨 START REACT FRONTEND ONLY
:: ============================================

echo.
echo ========================================
echo   🎨 Starting React Frontend...
echo ========================================
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Set paths
set "GAME_DIR=%SCRIPT_DIR%\cultivation-sim"
set "UI_DIR=%GAME_DIR%\cultivation-ui"

:: Check if UI directory exists
if not exist "%UI_DIR%" (
    echo ❌ Error: cultivation-ui directory not found!
    echo    Expected: %UI_DIR%
    echo.
    pause
    exit /b 1
)

:: Check if package.json exists
if not exist "%UI_DIR%\package.json" (
    echo ❌ Error: package.json not found!
    echo    Expected: %UI_DIR%\package.json
    echo.
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js not found!
    echo    Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: Check if node_modules exists
if not exist "%UI_DIR%\node_modules" (
    echo.
    echo ⚠️  node_modules not found. Installing dependencies...
    echo.
    cd /d "%UI_DIR%"
    if errorlevel 1 (
        echo ❌ Error: Cannot change to UI directory!
        echo    Path: %UI_DIR%
        echo.
        pause
        exit /b 1
    )
    
    call npm install
    if errorlevel 1 (
        echo ❌ Error: npm install failed!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ Dependencies installed!
    echo.
)

:: Clean port 5173
echo 🔧 Cleaning port 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

:: Start frontend
echo.
echo ========================================
echo   🚀 Starting React Dev Server...
echo ========================================
echo.
echo 📍 Frontend: http://localhost:5173
echo.
echo ⚠️  Keep this window open!
echo    Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

:: Change to UI directory and start
cd /d "%UI_DIR%"
if errorlevel 1 (
    echo ❌ Error: Cannot change to UI directory!
    echo    Path: %UI_DIR%
    echo.
    pause
    exit /b 1
)

:: Start npm run dev
call npm run dev

pause

