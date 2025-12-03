@echo off
chcp 65001 >nul
title Cultivation Simulator - Backend Only

echo ========================================
echo   Starting Backend Server Only
echo ========================================
echo.

set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
cd /d "%GAME_DIR%"

:: Clean port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Start server
echo Starting server on http://localhost:8001
echo.
start "Cultivation Simulator - Backend" cmd /k "cd /d "%GAME_DIR%" && python -u server.py"

timeout /t 3 >nul
echo.
echo ✅ Server started!
echo.
echo 📍 Server: http://localhost:8001
echo 📍 API docs: http://localhost:8001/docs
echo.
echo Open game.html in browser or run OPEN_GAME_HTML.bat
echo.
pause

