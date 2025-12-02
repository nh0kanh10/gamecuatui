@echo off
REM Neurosymbolic Text Adventure - Full Setup Script
echo ========================================
echo   Neurosymbolic Game - Full Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/6] Creating Python virtual environment...
if not exist venv (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)

echo.
echo [2/6] Activating venv and upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q

echo.
echo [3/6] Installing Python dependencies...
echo   This may take 5-10 minutes...
pip install -r requirements.txt -q

echo.
echo [4/6] Checking Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo   WARNING: Ollama not running!
    echo   Please start Ollama: ollama serve
) else (
    echo   Ollama is running
    ollama list
)

echo.
echo [5/6] Creating project structure...
mkdir engine 2>nul
mkdir engine\core 2>nul
mkdir engine\ai 2>nul
mkdir engine\systems 2>nul
mkdir engine\utils 2>nul
mkdir data 2>nul
mkdir data\lore 2>nul
mkdir logs 2>nul
echo   Directories created

echo.
echo [6/6] Checking .env file...
if not exist .env (
    echo   Creating .env template...
    echo GEMINI_API_KEY=your_api_key_here > .env
    echo GEMINI_MODEL=gemini-2.0-flash-exp >> .env
    echo OLLAMA_MODEL=qwen2.5:3b >> .env
    echo.
    echo   WARNING: Please edit .env and add your Gemini API key!
) else (
    echo   .env file exists
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Dependencies installed:
pip list | findstr "esper pydantic fastapi ollama google-generative"
echo.
echo Next steps:
echo   1. Edit .env file and add GEMINI_API_KEY
echo   2. Ensure Ollama is running: ollama serve
echo   3. Start implementing Phase 1 (see task.md)
echo.
echo Quick verification:
echo   python -c "import esper, pydantic, fastapi; print('All core packages OK')"
echo.
pause
