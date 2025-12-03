@echo off
chcp 65001 >nul
title Cultivation Simulator - React Frontend (Fixed)

:: ============================================
:: 🎨 START REACT FRONTEND - FIXED VERSION
:: ============================================

:: Use pushd/popd for reliable path handling
pushd "%~dp0"

:: Set paths (relative to script location)
set "GAME_DIR=%~dp0cultivation-sim"
set "UI_DIR=%GAME_DIR%\cultivation-ui"

:: Verify paths
if not exist "%UI_DIR%" (
    echo ❌ Error: cultivation-ui not found at:
    echo    %UI_DIR%
    popd
    pause
    exit /b 1
)

if not exist "%UI_DIR%\package.json" (
    echo ❌ Error: package.json not found at:
    echo    %UI_DIR%\package.json
    popd
    pause
    exit /b 1
)

:: Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js not found in PATH
    popd
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "%UI_DIR%\node_modules" (
    echo.
    echo 📦 Installing dependencies...
    pushd "%UI_DIR%"
    call npm install
    if errorlevel 1 (
        echo ❌ npm install failed!
        popd
        popd
        pause
        exit /b 1
    )
    popd
)

:: Clean port 5173
echo.
echo 🔧 Cleaning port 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start frontend in new window
echo.
echo 🚀 Starting React Dev Server...
echo 📍 Will be available at: http://localhost:5173
echo.

:: Use quoted path in start command
start "Cultivation Simulator - Frontend" cmd /k "cd /d "%UI_DIR%" && npm run dev"

:: Wait a bit then open browser
timeout /t 3 >nul
start http://localhost:5173

popd

echo.
echo ✅ Frontend should be starting!
echo    Check the new window that opened.
echo.
pause

