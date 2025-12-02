@echo off
echo Installing requirements...
echo.

REM Change to parent directory where requirements.txt is
cd /d "%~dp0"
cd ..

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Installing from: %CD%\requirements.txt
echo.
echo NOTE: ChromaDB and sentence-transformers are optional (not needed for Simple Memory System)
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Some packages failed to install.
    echo This might be okay if they are optional dependencies.
    echo.
    echo Try installing core packages manually:
    echo   pip install fastapi uvicorn python-dotenv google-generativeai nicegui
    echo.
)

echo.
echo Done! You can now run the game.
pause
