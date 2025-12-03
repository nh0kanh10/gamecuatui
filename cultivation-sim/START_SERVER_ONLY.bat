@echo off
chcp 65001 >nul
title Cultivation Simulator - Server Only
color 0A

echo.
echo ========================================
echo   🚀 KHỞI ĐỘNG SERVER (CHỈ SERVER)
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    pause
    exit /b 1
)

:: Check .env
if not exist ".env" (
    echo ❌ File .env không tồn tại!
    echo Vui lòng tạo file .env với GEMINI_API_KEY
    pause
    exit /b 1
)

:: Kill existing server
echo Đang dọn dẹp port 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Start server
echo.
echo 🚀 Đang khởi động server...
echo 📍 Server: http://localhost:8001
echo 📍 API docs: http://localhost:8001/docs
echo.
echo ⚠️  Giữ cửa sổ này mở!
echo Nhấn Ctrl+C để dừng server
echo.
echo ========================================
echo.

python -u server.py

pause

