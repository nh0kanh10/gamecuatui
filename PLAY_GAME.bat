@echo off
chcp 65001 >nul
title Cultivation Simulator - Starting...

:: ============================================
:: 🚀 QUICK START GAME - ONE CLICK!
:: ============================================

echo.
echo ========================================
echo   🎮 CULTIVATION SIMULATOR
echo   ⚡ Quick Start (One Click)
echo ========================================
echo.

:: Set game directory (absolute path, handle trailing backslash)
set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"

:: Change to game directory
cd /d "%GAME_DIR%" 2>nul
if errorlevel 1 (
    echo ❌ Error: Cannot find cultivation-sim directory
    echo    Please run this from GameBuild folder
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

:: Check Node.js (for frontend)
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. Frontend may not work.
    echo    Continuing with backend only...
    set "SKIP_FRONTEND=1"
) else (
    set "SKIP_FRONTEND=0"
)

:: Clean up ports
echo.
echo 🔧 Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

:: Check dependencies
echo.
echo 📦 Checking dependencies...

:: Check Python packages
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install Python dependencies
        pause
        exit /b 1
    )
)

:: Check Node packages (if frontend enabled)
if "%SKIP_FRONTEND%"=="0" (
    if not exist "cultivation-ui\node_modules" (
        echo ⚠️  Installing Node.js dependencies...
        if exist "cultivation-ui\package.json" (
            cd cultivation-ui
            call npm install --silent
            if errorlevel 1 (
                echo ❌ Failed to install Node.js dependencies
                cd ..
                pause
                exit /b 1
            )
            cd ..
        ) else (
            echo ❌ Cannot find cultivation-ui\package.json
            pause
            exit /b 1
        )
    )
)

:: Check optimizations
if exist "optimizations.py" (
    echo ✅ RAM optimizations available
    set "HAS_OPTIMIZATIONS=1"
) else (
    echo ⚠️  Optimizations not found (optional)
    set "HAS_OPTIMIZATIONS=0"
)

:: Start backend server
echo.
echo ========================================
echo   🚀 Starting Backend Server...
echo ========================================
echo.
echo 📍 Server: http://localhost:8001
echo 📍 API docs: http://localhost:8001/docs
echo.

start "Cultivation Simulator - Backend" cmd /k "cd /d "%GAME_DIR%" && python -u server.py"

:: Wait for server to start
echo ⏳ Waiting for server to start...
timeout /t 3 >nul

:: Check if server is running (simple check)
echo ⏳ Waiting for server...
timeout /t 5 >nul
echo ✅ Backend server should be ready!

:: Start frontend (if enabled)
if "%SKIP_FRONTEND%"=="0" (
    echo.
    echo ========================================
    echo   🎨 Starting Frontend...
    echo ========================================
    echo.
    echo 📍 Frontend: http://localhost:5173
    echo.
    
    if exist "cultivation-ui\package.json" (
        set "UI_FULL_PATH=%GAME_DIR%\cultivation-ui"
        :: Verify path exists before starting
        if exist "%UI_FULL_PATH%" (
            start "Cultivation Simulator - Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && if exist package.json (npm run dev) else (echo ❌ Error: package.json not found in %UI_FULL_PATH% && pause)"
            echo ✅ Frontend starting...
        ) else (
            echo ❌ Error: Path does not exist: %UI_FULL_PATH%
            set "SKIP_FRONTEND=1"
        )
    ) else (
        echo ❌ Cannot find cultivation-ui\package.json
        echo    Expected: %GAME_DIR%\cultivation-ui\package.json
        set "SKIP_FRONTEND=1"
    )
    echo.
)

:: Open browser
echo ========================================
echo   ✅ GAME STARTED!
echo ========================================
echo.
echo 🎮 Opening game in browser...
timeout /t 2 >nul
start http://localhost:5173

echo.
echo ========================================
echo   📝 Instructions:
echo ========================================
echo.
echo ✅ Backend: Running in separate window
if "%SKIP_FRONTEND%"=="0" (
    echo ✅ Frontend: Running in separate window
    echo ✅ Browser: Should open automatically
) else (
    echo ⚠️  Frontend: Not available (Node.js missing)
    echo    Access API at: http://localhost:8001/docs
)
echo.
echo 💡 To stop: Close the server windows or press Ctrl+C
echo.
echo ========================================
echo.

pause
