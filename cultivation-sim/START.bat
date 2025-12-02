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
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    pause
    exit /b 1
)

:: Check .env
if not exist .env (
    echo ⚠️  Creating .env from template...
    if exist ..\.env.template (
        copy ..\.env.template .env >nul
    )
    echo    Please add GEMINI_API_KEY to .env
    timeout /t 2 >nul
)

:: Install dependencies
echo [1/2] Installing dependencies...
pip install -q -r requirements.txt 2>nul

:: Start server
echo [2/2] Starting server...
echo.
echo 📍 Server: http://localhost:8001
echo 📍 API Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop
echo.

python server.py

