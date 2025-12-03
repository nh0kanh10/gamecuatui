@echo off
chcp 65001 >nul
title Cultivation Simulator - Quick Test
color 0A

echo.
echo ========================================
echo   🧪 QUICK TEST - Cultivation Simulator
echo ========================================
echo.

cd /d "%~dp0"

:: Test 1: Python import
echo [Test 1/5] Kiểm tra Python imports...
python -c "from game import CultivationSimulator; print('✅ Game import OK')" 2>&1
if errorlevel 1 (
    echo ❌ Lỗi import game!
    pause
    exit /b 1
)

:: Test 2: Database
echo.
echo [Test 2/5] Kiểm tra Database...
python -c "from database import init_database; import os; test_db = 'data/saves/test_quick.db'; os.makedirs('data/saves', exist_ok=True); init_database(test_db); print('✅ Database OK')" 2>&1
if errorlevel 1 (
    echo ❌ Lỗi database!
    pause
    exit /b 1
)

:: Test 3: Server import
echo.
echo [Test 3/5] Kiểm tra Server import...
python -c "import server; print('✅ Server import OK')" 2>&1
if errorlevel 1 (
    echo ❌ Lỗi server import!
    pause
    exit /b 1
)

:: Test 4: Check .env
echo.
echo [Test 4/5] Kiểm tra .env...
if exist ".env" (
    echo ✅ File .env tồn tại
) else (
    echo ⚠️  File .env không tồn tại (sẽ được tạo khi chạy START_GAME.bat)
)

:: Test 5: Check node_modules
echo.
echo [Test 5/5] Kiểm tra Node.js dependencies...
cd cultivation-ui
if exist "node_modules" (
    echo ✅ node_modules tồn tại
) else (
    echo ⚠️  node_modules chưa có (sẽ được cài khi chạy START_GAME.bat)
)
cd ..

echo.
echo ========================================
echo   ✅ TẤT CẢ TEST ĐÃ HOÀN THÀNH!
echo ========================================
echo.
echo 💡 Bạn có thể chạy START_GAME.bat để khởi động game
echo.
pause

