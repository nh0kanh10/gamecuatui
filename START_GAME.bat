@echo off
echo ========================================
echo   Starting Game - Full Stack
echo ========================================
echo.

REM Check if server is running
netstat -ano | findstr :8000 >nul 2>&1
if errorlevel 1 (
    echo [1/2] Starting server...
    start "Game Server" cmd /k "python server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo [1/2] Server already running on port 8000
)

REM Start UI
echo [2/2] Starting React UI...
cd react-ui
if not exist "node_modules" (
    echo Installing React UI dependencies...
    call npm install
)
start "Game UI" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Game Started!
echo ========================================
echo.
echo Server: http://localhost:8000
echo UI: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul

