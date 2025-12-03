@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Cultivation Simulator - Start Game
color 0B

echo.
echo ========================================
echo   CULTIVATION SIMULATOR
echo   Tu Tien Life Simulation
echo ========================================
echo.

:: Change to script directory (handles drive change)
pushd "%~dp0"

:: Check Python
echo [1/5] Kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python khong duoc tim thay!
    echo Vui long cai dat Python 3.8+ va them vao PATH
    popd
    pause
    exit /b 1
)
python --version
echo Python OK

:: Check Node.js
echo.
echo [2/5] Kiem tra Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js khong duoc tim thay!
    echo Vui long cai dat Node.js va them vao PATH
    echo.
    echo Nhan phim bat ky de thoat...
    popd
    pause >nul
    exit /b 1
)
node --version
echo Node.js OK

:: Check .env file
echo.
echo [3/5] Kiem tra file .env...
if not exist ".env" (
    echo File .env khong ton tai!
    echo Tao file .env voi GEMINI_API_KEY...
    (
        echo GEMINI_API_KEY=your_api_key_here
    ) > .env
    echo Da tao file .env
    echo.
    echo QUAN TRONG: VUI LONG THEM GEMINI_API_KEY VAO FILE .env TRUOC KHI CHOI!
    echo.
    echo Ban co the:
    echo   1. Mo file .env va thay "your_api_key_here" bang API key that
    echo   2. Hoac chay: echo GEMINI_API_KEY=your_key ^> .env
    echo.
    timeout /t 5 >nul
) else (
    echo File .env da ton tai
    findstr /C:"GEMINI_API_KEY" .env >nul 2>&1
    if errorlevel 1 (
        echo File .env khong co GEMINI_API_KEY!
        echo Vui long them GEMINI_API_KEY vao file .env
        timeout /t 3 >nul
    ) else (
        findstr /C:"your_api_key_here" .env >nul 2>&1
        if not errorlevel 1 (
            echo GEMINI_API_KEY van la placeholder!
            echo Vui long thay "your_api_key_here" bang API key that
            timeout /t 3 >nul
        ) else (
            echo GEMINI_API_KEY da duoc cau hinh
        )
    )
)

:: Install Python dependencies
echo.
echo [4/5] Cai dat Python dependencies...
pip install -q -r requirements.txt 2>&1
if errorlevel 1 (
    echo Loi cai dat Python dependencies!
    echo.
    echo Vui long kiem tra loi o tren
    popd
    pause
    exit /b 1
)
echo Python dependencies OK

:: Install Node.js dependencies
echo.
echo [5/5] Cai dat Node.js dependencies...
pushd cultivation-ui
if exist "node_modules" (
    echo node_modules da ton tai, bo qua
    goto :skip_npm_install
)
echo Dang cai dat npm packages (lan dau co the mat vai phut)
call npm install
if errorlevel 1 (
    echo Loi cai dat Node.js dependencies!
    echo.
    echo Vui long kiem tra loi o tren
    popd
    popd
    pause
    exit /b 1
)
:skip_npm_install
popd
echo Node.js dependencies OK

:: Kill existing processes on port 8001 and 5173
echo.
echo Dang don dep ports...
echo Kiem tra port 8001...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo   Dang dong process %%a tren port 8001...
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 echo   Da dong process %%a
)
echo Kiem tra port 5173...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo   Dang dong process %%a tren port 5173...
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 echo   Da dong process %%a
)
timeout /t 3 /nobreak >nul

:: Get absolute path for server command
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Start Python server
echo.
echo ========================================
echo   KHOI DONG GAME...
echo ========================================
echo.
echo Server: http://localhost:8001
echo UI:     http://localhost:5173
echo.
echo Dang khoi dong backend server...
echo.
echo Luu y: Cua so "Cultivation Simulator Server" se mo rieng
echo    Neu co loi, ban se thay trong cua so do
echo.
start "Cultivation Simulator Server" cmd /k "cd /d %SCRIPT_DIR% && python -u server.py"
timeout /t 8 /nobreak >nul

:: Check if server is actually running
echo Kiem tra server da khoi dong...
timeout /t 2 /nobreak >nul
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Server dang chay tren port 8001 (PID: %%a)
    goto :server_running
)
echo Server chua khoi dong hoac da crash
echo    Vui long kiem tra cua so "Cultivation Simulator Server" de xem loi
echo.
timeout /t 3 /nobreak >nul

:server_running

:: Start React UI
echo.
echo Dang khoi dong UI...
echo Luu y: Cua so "Cultivation Simulator UI" se mo rieng
set "UI_DIR=%SCRIPT_DIR%\cultivation-ui"
start "Cultivation Simulator UI" cmd /k "cd /d %UI_DIR% && npm run dev"

:: Wait for servers to start
echo.
echo Dang cho servers khoi dong (10 giay)...
timeout /t 10 /nobreak >nul

:: Check if server is running (skip if curl not available)
echo.
echo Dang kiem tra server...
timeout /t 2 /nobreak >nul
where curl >nul 2>&1
if not errorlevel 1 (
    curl -s http://localhost:8001/health >nul 2>&1
    if errorlevel 1 (
        echo Server chua san sang, doi them 5 giay...
        timeout /t 5 /nobreak >nul
    )
) else (
    echo curl khong co san, bo qua health check
)

:: Open browser
echo.
echo Dang mo trinh duyet...
start http://localhost:5173

echo.
echo ========================================
echo   GAME DA KHOI DONG THANH CONG!
echo ========================================
echo.
echo Huong dan:
echo    1. Chon gioi tinh, thien phu, chung toc, boi canh
echo    2. Nhan "Bat Dau Tu Luyen" de tao nhan vat
echo    3. Chon lua chon (1-6) de tiep tuc cau chuyen
echo.
echo Luu y: Giu 2 cua so (Server va UI) mo trong khi choi!
echo.
echo De dung game: Dong 2 cua so Server va UI
echo.
echo Neu game khong chay duoc:
echo    - Kiem tra cua so "Cultivation Simulator Server" xem co loi khong
echo    - Kiem tra cua so "Cultivation Simulator UI" xem co loi khong
echo    - Chay CHECK_SERVER.bat de kiem tra server status
echo.
echo Nhan phim bat ky de dong cua so nay (game van chay)...
popd
pause

