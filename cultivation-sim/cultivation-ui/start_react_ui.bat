@echo off
echo Starting React UI...
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting dev server...
echo UI will open at: http://localhost:5173
echo.
call npm run dev

