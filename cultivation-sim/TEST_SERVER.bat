@echo off
chcp 65001 >nul
title Test Server - Cultivation Simulator
color 0E

echo.
echo ========================================
echo   🧪 TEST SERVER - Cultivation Simulator
echo ========================================
echo.

cd /d "%~dp0"

:: Kill existing server
echo [1/3] Dọn dẹp port 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    echo Đang đóng process %%a...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Test server import and initialization
echo.
echo [2/3] Test server import và khởi tạo...
python -c "import sys; sys.path.insert(0, '.'); from server import app; print('✅ Server import OK'); from game import CultivationSimulator; g = CultivationSimulator('test_server'); print('✅ Game instance OK')" 2>&1
if errorlevel 1 (
    echo.
    echo ❌ LỖI KHI KHỞI TẠO SERVER!
    echo.
    echo Vui lòng kiểm tra lỗi ở trên và sửa trước khi chạy START_GAME.bat
    echo.
    pause
    exit /b 1
)

:: Try to start server for 5 seconds
echo.
echo [3/3] Test khởi động server (5 giây)...
start /B python server.py > server_test.log 2>&1
timeout /t 5 /nobreak >nul

:: Check if server is running
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    echo ✅ Server đang chạy trên port 8001 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
    goto :success
)

echo ❌ Server không khởi động được!
echo.
echo Kiểm tra server_test.log để xem lỗi:
type server_test.log 2>nul
echo.
pause
exit /b 1

:success
echo.
echo ========================================
echo   ✅ SERVER TEST THÀNH CÔNG!
echo ========================================
echo.
echo Bạn có thể chạy START_GAME.bat để khởi động game
echo.
pause

