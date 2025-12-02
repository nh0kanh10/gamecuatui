@echo off
chcp 65001 >nul
title Game Engine - Auto Start
color 0A

echo.
echo ========================================
echo    🎮 GAME ENGINE - AUTO START 🎮
echo ========================================
echo.

:: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python OK

:: Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js
    pause
    exit /b 1
)
echo ✅ Node.js OK

:: Check .env file
echo [3/5] Checking environment...
if not exist .env (
    echo ⚠️  .env file not found!
    echo    Creating .env.template...
    if exist .env.template (
        copy .env.template .env >nul
        echo    ✅ Created .env from template
        echo    ⚠️  Please edit .env and add your GEMINI_API_KEY!
        timeout /t 3 >nul
    ) else (
        echo    ❌ .env.template not found!
        pause
        exit /b 1
    )
)
echo ✅ Environment OK

:: Check API Key
findstr /C:"GEMINI_API_KEY" .env >nul 2>&1
if errorlevel 1 (
    echo ⚠️  GEMINI_API_KEY not found in .env!
    echo    Please add your API key to .env file
    pause
    exit /b 1
)
echo ✅ API Key found

:: Install Python dependencies
echo [4/5] Installing Python dependencies...
pip install -q -r requirements.txt 2>nul
if errorlevel 1 (
    echo ⚠️  Some packages may need manual installation
)
echo ✅ Dependencies OK

:: Install React UI dependencies
echo [5/5] Installing React UI dependencies...
if not exist react-ui\node_modules (
    echo    Installing npm packages (first time, may take a while)...
    cd react-ui
    call npm install --silent
    cd ..
    echo    ✅ React UI dependencies installed
) else (
    echo ✅ React UI dependencies OK
)

echo.
echo ========================================
echo    🚀 STARTING GAME ENGINE...
echo ========================================
echo.

:: Kill existing processes on port 8000
echo [Cleanup] Checking port 8000...
netstat -ano | findstr :8000 >nul 2>&1
if not errorlevel 1 (
    echo    Port 8000 is in use, killing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)
echo ✅ Port 8000 ready

:: Start Python server in new window
echo [Server] Starting Python server...
start "Game Server" cmd /k "python server.py"
timeout /t 3 >nul

:: Wait for server to be ready
echo [Server] Waiting for server to start...
:wait_server
timeout /t 1 >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    goto wait_server
)
echo ✅ Server is running!

:: Start React UI in new window
echo [UI] Starting React UI...
cd react-ui
start "React UI" cmd /k "npm run dev"
cd ..
timeout /t 5 >nul

:: Open browser
echo [Browser] Opening game in browser...
timeout /t 2 >nul
start http://localhost:5173

echo.
echo ========================================
echo    ✅ GAME STARTED SUCCESSFULLY!
echo ========================================
echo.
echo 📍 Server: http://localhost:8000
echo 📍 UI:     http://localhost:5173
echo.
echo 💡 Tips:
echo    - Game will open in your browser automatically
echo    - Keep these windows open while playing
echo    - Press Ctrl+C in server window to stop
echo.
echo Press any key to close this window...
pause >nul

