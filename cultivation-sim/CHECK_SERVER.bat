@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Check Server Status

echo.
echo ========================================
echo   CHECK SERVER STATUS
echo ========================================
echo.

cd /d "%~dp0"

:: Check if port 8001 is in use
echo [1/3] Checking port 8001...
netstat -aon | findstr :8001 | findstr LISTENING >nul 2>&1
if errorlevel 1 (
    echo   Port 8001: NOT IN USE
    echo   Server is NOT running!
    goto :check_ui
) else (
    echo   Port 8001: IN USE
    echo   Server appears to be running
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
        echo   Process ID: %%a
    )
)

:: Check if server responds
echo.
echo [2/3] Testing server health endpoint...
where curl >nul 2>&1
if not errorlevel 1 (
    curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://localhost:8001/health 2>nul
    if errorlevel 1 (
        echo   Server is NOT responding!
    ) else (
        echo   Server is responding
    )
) else (
    echo   curl not available, skipping health check
    echo   You can test manually: http://localhost:8001/health
)

:check_ui
:: Check if port 5173 is in use
echo.
echo [3/3] Checking port 5173 (UI)...
netstat -aon | findstr :5173 | findstr LISTENING >nul 2>&1
if errorlevel 1 (
    echo   Port 5173: NOT IN USE
    echo   UI is NOT running!
) else (
    echo   Port 5173: IN USE
    echo   UI appears to be running
)

:: Check log files
echo.
echo ========================================
echo   RECENT LOG FILES
echo ========================================
if exist "logs\*.log" (
    echo Recent log files:
    dir /b /o-d logs\*.log 2>nul | head -n 3
    echo.
    echo To view latest log:
    echo   type logs\server_*.log ^| more
) else (
    echo No log files found in logs\ directory
)

echo.
echo ========================================
echo   TROUBLESHOOTING
echo ========================================
echo.
echo If server is not running:
echo   1. Run START_GAME.bat
echo   2. Or run START_SERVER_ONLY.bat
echo   3. Check the server window for errors
echo.
echo If server is running but not responding:
echo   1. Check log files in logs\ directory
echo   2. Look for ERROR messages
echo   3. Check if GEMINI_API_KEY is set in .env
echo.
pause
