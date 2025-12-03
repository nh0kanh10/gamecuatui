@echo off
echo Opening game in browser...
start "" "%~dp0cultivation-sim\game.html"
echo.
echo ✅ Game HTML opened!
echo.
echo Make sure backend server is running on port 8001
echo If not, run: START.bat or QUICK_START.bat
echo.
pause

