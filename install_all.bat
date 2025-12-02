@echo off
echo ========================================
echo   Installing Game Dependencies
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo Python found!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install core dependencies one by one
echo Installing core dependencies...
echo.

python -m pip install fastapi --quiet
if errorlevel 1 (
    echo WARNING: Failed to install fastapi
) else (
    echo [OK] fastapi
)

python -m pip install uvicorn --quiet
if errorlevel 1 (
    echo WARNING: Failed to install uvicorn
) else (
    echo [OK] uvicorn
)

python -m pip install python-dotenv --quiet
if errorlevel 1 (
    echo WARNING: Failed to install python-dotenv
) else (
    echo [OK] python-dotenv
)

python -m pip install google-generativeai --quiet
if errorlevel 1 (
    echo WARNING: Failed to install google-generativeai
) else (
    echo [OK] google-generativeai
)

python -m pip install nicegui --quiet
if errorlevel 1 (
    echo WARNING: Failed to install nicegui
) else (
    echo [OK] nicegui
)

python -m pip install networkx --quiet
if errorlevel 1 (
    echo WARNING: Failed to install networkx
) else (
    echo [OK] networkx
)

python -m pip install loguru --quiet
if errorlevel 1 (
    echo WARNING: Failed to install loguru
) else (
    echo [OK] loguru
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file with GEMINI_API_KEY
echo 2. Run: python server.py
echo 3. Or run: play\start_game_ui.bat
echo.
pause

