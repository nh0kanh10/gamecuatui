@echo off
chcp 65001 >nul
title Cultivation Simulator - Start Game
color 0B

echo.
echo ========================================
echo   🌟 CULTIVATION SIMULATOR 🌟
echo   Tu Tiên Life Simulation
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python
echo [1/5] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    echo Vui lòng cài đặt Python 3.8+ và thêm vào PATH
    pause
    exit /b 1
)
python --version
echo ✅ Python OK

:: Check Node.js
echo.
echo [2/5] Kiểm tra Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js không được tìm thấy!
    echo Vui lòng cài đặt Node.js và thêm vào PATH
    pause
    exit /b 1
)
node --version
echo ✅ Node.js OK

:: Check .env file
echo.
echo [3/5] Kiểm tra file .env...
if not exist ".env" (
    echo ⚠️  File .env không tồn tại!
    echo Tạo file .env với GEMINI_API_KEY...
    (
        echo GEMINI_API_KEY=your_api_key_here
    ) > .env
    echo ✅ Đã tạo file .env
    echo ⚠️  VUI LÒNG THÊM GEMINI_API_KEY VÀO FILE .env TRƯỚC KHI CHƠI!
    timeout /t 3 >nul
) else (
    echo ✅ File .env đã tồn tại
)

:: Install Python dependencies
echo.
echo [4/5] Cài đặt Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi cài đặt Python dependencies!
    pause
    exit /b 1
)
echo ✅ Python dependencies OK

:: Install Node.js dependencies
echo.
echo [5/5] Cài đặt Node.js dependencies...
cd cultivation-ui
if not exist "node_modules" (
    echo Đang cài đặt npm packages (lần đầu có thể mất vài phút)...
    call npm install
    if errorlevel 1 (
        echo ❌ Lỗi cài đặt Node.js dependencies!
        cd ..
        pause
        exit /b 1
    )
) else (
    echo node_modules đã tồn tại, bỏ qua...
)
cd ..
echo ✅ Node.js dependencies OK

:: Kill existing processes on port 8001 and 5173
echo.
echo Đang dọn dẹp ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    echo Đang đóng process %%a trên port 8001...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo Đang đóng process %%a trên port 5173...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Start Python server
echo.
echo ========================================
echo   🚀 KHỞI ĐỘNG GAME...
echo ========================================
echo.
echo 📍 Server: http://localhost:8001
echo 📍 UI:     http://localhost:5173
echo.
echo ⏳ Đang khởi động backend server...
start "Cultivation Simulator Server" cmd /k "cd /d %~dp0 && python server.py"
timeout /t 3 /nobreak >nul

:: Start React UI
echo ⏳ Đang khởi động UI...
cd cultivation-ui
start "Cultivation Simulator UI" cmd /k "npm run dev"
cd ..

:: Wait for servers to start
echo.
echo ⏳ Đang chờ servers khởi động...
timeout /t 8 /nobreak >nul

:: Open browser
echo.
echo ✅ Đang mở trình duyệt...
start http://localhost:5173

echo.
echo ========================================
echo   ✅ GAME ĐÃ KHỞI ĐỘNG THÀNH CÔNG!
echo ========================================
echo.
echo 💡 Hướng dẫn:
echo    1. Chọn giới tính, thiên phú, chủng tộc, bối cảnh
echo    2. Nhấn "Bắt Đầu Tu Luyện" để tạo nhân vật
echo    3. Chọn lựa chọn (1-6) để tiếp tục câu chuyện
echo.
echo ⚠️  Lưu ý: Giữ 2 cửa sổ (Server và UI) mở trong khi chơi!
echo.
echo Nhấn phím bất kỳ để đóng cửa sổ này...
pause >nul

