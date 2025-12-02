@echo off
REM Quick start script for AI text adventure
echo ========================================
echo   🎮 AI TEXT ADVENTURE - QUICK START
echo ========================================
echo.

REM Change to script directory, then go to parent
cd /d "%~dp0"
cd ..

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in parent directory!
    echo Please run this script from the play folder.
    pause
    exit /b 1
)

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
echo Starting game from: %CD%
echo.
python play\play.py
