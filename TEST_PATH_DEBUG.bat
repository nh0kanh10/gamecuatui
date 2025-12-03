@echo off
chcp 65001 >nul
echo ========================================
echo   PATH DEBUG TEST
echo ========================================
echo.

echo [1] Current directory:
echo %CD%
echo.

echo [2] Script directory (%%~dp0):
echo %~dp0
echo.

echo [3] Test GAME_DIR setup:
set "GAME_DIR=%~dp0"
echo Original: "%GAME_DIR%"
set "GAME_DIR=%GAME_DIR:~0,-1%"
echo After strip: "%GAME_DIR%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
echo Final GAME_DIR: "%GAME_DIR%"
echo.

echo [4] Test if cultivation-sim exists:
if exist "%GAME_DIR%" (
    echo ✅ cultivation-sim exists
) else (
    echo ❌ cultivation-sim NOT found
)
echo.

echo [5] Change to game directory:
cd /d "%GAME_DIR%" 2>nul
if errorlevel 1 (
    echo ❌ Cannot change to %GAME_DIR%
) else (
    echo ✅ Changed to: %CD%
)
echo.

echo [6] Test pushd to cultivation-ui:
if exist "cultivation-ui" (
    echo ✅ cultivation-ui folder exists
    pushd cultivation-ui
    if errorlevel 1 (
        echo ❌ pushd failed
    ) else (
        echo ✅ pushd successful
        echo Current in pushd: %CD%
        set "UI_FULL_PATH=%CD%"
        echo UI_FULL_PATH set to: "%UI_FULL_PATH%"
        popd
        echo ✅ popd successful
        echo After popd: %CD%
    )
) else (
    echo ❌ cultivation-ui folder NOT found
)
echo.

echo [7] Test start command (dry run):
if defined UI_FULL_PATH (
    echo Would run: start "Frontend" cmd /k "cd /d "%UI_FULL_PATH%" && npm run dev"
    echo.
    echo Testing path validity:
    if exist "%UI_FULL_PATH%" (
        echo ✅ Path exists: "%UI_FULL_PATH%"
    ) else (
        echo ❌ Path does NOT exist: "%UI_FULL_PATH%"
    )
    echo.
    echo Testing if package.json exists:
    if exist "%UI_FULL_PATH%\package.json" (
        echo ✅ package.json found
    ) else (
        echo ❌ package.json NOT found
    )
) else (
    echo ❌ UI_FULL_PATH not set
)
echo.

echo ========================================
echo   END OF TEST
echo ========================================
pause

