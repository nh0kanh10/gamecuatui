@echo off
echo ========================================
echo   Starting Game - React UI
echo ========================================
echo.

cd /d "%~dp0"

REM Check if server is running
netstat -ano | findstr :8000 >nul 2>&1
if errorlevel 1 (
    echo [1/2] Starting server...
    start "Game Server" cmd /k "python server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo [1/2] Server already running on port 8000
)

REM Start React UI
echo [2/2] Starting React UI...
cd react-ui

REM Check if dependencies are installed
if not exist "node_modules" (
    echo Installing React UI dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        echo Make sure Node.js is installed: https://nodejs.org/
        pause
        exit /b 1
    )
)

start "Game UI" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Game Started!
echo ========================================
echo.
echo Server: http://localhost:8000
echo React UI: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul

