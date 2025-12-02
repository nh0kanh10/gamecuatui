@echo off
cd /d "%~dp0"
echo Installing React UI dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    echo Make sure Node.js is installed: https://nodejs.org/
    pause
    exit /b 1
)
echo.
echo ✅ Dependencies installed successfully!
pause

