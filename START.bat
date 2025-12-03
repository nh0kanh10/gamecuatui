@echo off
:: ============================================
:: 🎮 ONE-CLICK GAME LAUNCHER
:: ============================================
:: Just double-click this file to start!

set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
cd /d "%GAME_DIR%"

:: Quick start
echo Starting game...
start "Backend" cmd /k "cd /d "%GAME_DIR%" && python -u server.py"
timeout /t 3 >nul
if exist "cultivation-ui\node_modules" (
    set "UI_FULL_PATH=%GAME_DIR%\cultivation-ui"
    if exist "%UI_FULL_PATH%\package.json" (
        start "Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && if exist package.json (npm run dev) else (echo ❌ Error: package.json not found && pause)"
        timeout /t 2 >nul
        start http://localhost:5173
    ) else (
        echo ⚠️  Frontend: package.json not found
    )
)
echo Game started! Check the windows.
pause

