@echo off
echo Testing direct path method...
echo.

set "GAME_DIR=D:\GameBuild\cultivation-sim"
set "UI_FULL_PATH=%GAME_DIR%\cultivation-ui"

echo GAME_DIR: %GAME_DIR%
echo UI_FULL_PATH: %UI_FULL_PATH%
echo.

if exist "%UI_FULL_PATH%\package.json" (
    echo ✅ package.json found!
    echo.
    echo Testing start command...
    start "TEST" cmd /k "cd /d "%UI_FULL_PATH%" && cd && npm run dev"
) else (
    echo ❌ package.json NOT found at: %UI_FULL_PATH%\package.json
    echo.
    echo Checking if folder exists:
    if exist "%UI_FULL_PATH%" (
        echo ✅ Folder exists
        dir "%UI_FULL_PATH%"
    ) else (
        echo ❌ Folder does NOT exist
    )
)

pause

