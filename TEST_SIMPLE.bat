@echo off
echo Simple test - just change directory and run npm
cd /d "%~dp0cultivation-sim\cultivation-ui"
if errorlevel 1 (
    echo Failed to change directory
    pause
    exit /b 1
)
echo Current directory: %CD%
echo.
echo Running: npm run dev
npm run dev

