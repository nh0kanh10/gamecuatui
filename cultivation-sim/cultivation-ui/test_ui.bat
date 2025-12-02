@echo off
cd /d "%~dp0"

echo ========================================
echo   Testing React UI
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies first...
    call install.bat
    if errorlevel 1 exit /b 1
)

echo.
echo Starting React UI dev server...
echo UI will open at: http://localhost:5173
echo.
echo Make sure the game server is running on port 8000!
echo.
call npm run dev

