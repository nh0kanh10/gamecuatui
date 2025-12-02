@echo off
echo ========================================
echo   Quick Fix - Port 8000 + TailwindCSS
echo ========================================
echo.

REM Kill port 8000
echo [1/3] Killing process on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 2^>nul') do (
    echo   Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo   Done!
echo.

REM Fix TailwindCSS
echo [2/3] Fixing TailwindCSS...
cd game-ui
call npm uninstall @tailwindcss/postcss >nul 2>&1
call npm install -D tailwindcss@^3.4.0 >nul 2>&1
echo   Done!
cd ..
echo.

REM Clear cache
echo [3/3] Clearing cache...
if exist "game-ui\node_modules\.vite" rmdir /s /q "game-ui\node_modules\.vite" >nul 2>&1
if exist "game-ui\.svelte-kit" rmdir /s /q "game-ui\.svelte-kit" >nul 2>&1
echo   Done!
echo.

echo ========================================
echo   All Fixed!
echo ========================================
echo.
echo Next steps:
echo 1. Start server: python server.py
echo 2. Start UI: cd game-ui && npm run dev
echo.
pause

