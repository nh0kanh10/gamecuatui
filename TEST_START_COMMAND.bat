@echo off
chcp 65001 >nul
echo ========================================
echo   TEST START COMMAND
echo ========================================
echo.

cd /d "%~dp0cultivation-sim"
if errorlevel 1 (
    echo ❌ Cannot find cultivation-sim
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo [Test 1] Using pushd method:
pushd cultivation-ui
if not errorlevel 1 (
    set "UI_FULL_PATH=%CD%"
    echo UI_FULL_PATH: "%UI_FULL_PATH%"
    popd
    
    echo.
    echo Attempting to start frontend...
    start "TEST Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && echo Current dir: && cd && echo Running npm run dev... && npm run dev"
    echo.
    echo ✅ Command sent. Check the new window for errors.
) else (
    echo ❌ pushd failed
)

echo.
echo [Test 2] Using direct path:
set "DIRECT_PATH=%CD%\cultivation-ui"
echo DIRECT_PATH: "%DIRECT_PATH%"
if exist "%DIRECT_PATH%\package.json" (
    echo ✅ package.json found
    echo.
    echo Attempting to start with direct path...
    start "TEST Frontend 2" cmd /k "cd /d "%DIRECT_PATH%" && echo Current dir: && cd && echo Running npm run dev... && npm run dev"
    echo.
    echo ✅ Command sent. Check the new window for errors.
) else (
    echo ❌ package.json NOT found at "%DIRECT_PATH%\package.json"
)

echo.
echo ========================================
pause

