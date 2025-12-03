@echo off
chcp 65001 >nul
title Cultivation Simulator - Simple Start

echo ========================================
echo   Starting Game (Simple HTML)
echo ========================================
echo.

set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
cd /d "%GAME_DIR%"

:: Clean port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

:: Start server
echo [1/2] Starting backend server...
start "Backend" cmd /k "cd /d "%GAME_DIR%" && python -u server.py"

timeout /t 5 >nul

:: Open HTML
echo [2/2] Opening game in browser...
start "" "%GAME_DIR%\game.html"

echo.
echo ✅ Game started!
echo.
echo 📍 Server: http://localhost:8001
echo 📍 Game: game.html (opened in browser)
echo.
pause

