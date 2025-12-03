@echo off
chcp 65001 >nul
echo ========================================
echo   TEST FIXED PATH METHOD
echo ========================================
echo.

:: Setup GAME_DIR (same as in scripts)
set "GAME_DIR=%~dp0"
set "GAME_DIR=%GAME_DIR:~0,-1%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"

echo [1] GAME_DIR: "%GAME_DIR%"
echo.

:: Test UI_FULL_PATH
set "UI_FULL_PATH=%GAME_DIR%\cultivation-ui"
echo [2] UI_FULL_PATH: "%UI_FULL_PATH%"
echo.

:: Test if path exists
if exist "%UI_FULL_PATH%" (
    echo [3] ✅ Path exists: "%UI_FULL_PATH%"
) else (
    echo [3] ❌ Path does NOT exist: "%UI_FULL_PATH%"
)
echo.

:: Test if package.json exists
if exist "%UI_FULL_PATH%\package.json" (
    echo [4] ✅ package.json found at: "%UI_FULL_PATH%\package.json"
) else (
    echo [4] ❌ package.json NOT found at: "%UI_FULL_PATH%\package.json"
)
echo.

:: Test if node_modules exists
if exist "%UI_FULL_PATH%\node_modules" (
    echo [5] ✅ node_modules found
) else (
    echo [5] ⚠️  node_modules NOT found (need to run npm install)
)
echo.

:: Test start command (dry run)
echo [6] Would run:
echo     start "Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && npm run dev"
echo.

:: Actually test the start command
echo [7] Testing actual start command...
echo     Opening test window...
start "TEST Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && echo Current directory: && cd && echo. && echo Testing npm... && npm --version && echo. && if exist package.json (echo ✅ package.json found) else (echo ❌ package.json NOT found) && pause"

echo.
echo ✅ Test window opened. Check it for results.
echo.

echo ========================================
pause

