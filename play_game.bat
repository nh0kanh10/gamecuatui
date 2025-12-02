@echo off
REM Quick start script for AI text adventure
echo ========================================
echo   🎮 AI TEXT ADVENTURE - QUICK START
echo ========================================
echo.

REM Check Ollama
echo Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo   ❌ Ollama not running!
    echo   Please start: ollama serve
    echo.
    pause
    exit /b 1
)
echo   ✅ Ollama is running

echo.
echo Starting game...
echo.
venv\Scripts\python.exe play.py
