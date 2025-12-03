@echo off
:: Test path handling
set "GAME_DIR=%~dp0"
echo Original: "%GAME_DIR%"
set "GAME_DIR=%GAME_DIR:~0,-1%"
echo After strip: "%GAME_DIR%"
set "GAME_DIR=%GAME_DIR%\cultivation-sim"
echo Final: "%GAME_DIR%"
pause

