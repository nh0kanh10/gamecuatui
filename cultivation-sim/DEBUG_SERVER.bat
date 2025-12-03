@echo off
chcp 65001 >nul
title Debug Server - Cultivation Simulator
color 0C

echo.
echo ========================================
echo   🐛 DEBUG SERVER - Cultivation Simulator
echo ========================================
echo.

cd /d "%~dp0"

:: Test imports step by step
echo [1/6] Test import database...
python -c "from database import get_db, init_database; print('✅ database OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo [2/6] Test import agent...
python -c "from agent import CultivationAgent; print('✅ agent OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo [3/6] Test import memory...
python -c "from memory_3tier import Memory3Tier; print('✅ memory OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo [4/6] Test import game...
python -c "from game import CultivationSimulator; print('✅ game OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo [5/6] Test create game instance...
python -c "from game import CultivationSimulator; g = CultivationSimulator('debug_test'); print('✅ game instance OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo [6/6] Test import server...
python -c "import server; print('✅ server import OK')" 2>&1
if errorlevel 1 goto :error

echo.
echo ========================================
echo   ✅ TẤT CẢ IMPORTS OK!
echo ========================================
echo.
echo Bây giờ thử chạy server trực tiếp:
echo   python server.py
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo   ❌ LỖI PHÁT HIỆN!
echo ========================================
echo.
echo Vui lòng kiểm tra lỗi ở trên
echo.
pause
exit /b 1

