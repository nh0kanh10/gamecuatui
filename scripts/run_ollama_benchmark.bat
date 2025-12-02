@echo off
REM Quick benchmark with Ollama (no model download needed!)
echo ========================================
echo   Ollama Benchmark Quick Start
echo ========================================
echo.

REM Check if Ollama is running
ollama list >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not running!
    echo Please start Ollama first.
    pause
    exit /b 1
)

echo [1/3] Setting up Python environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2/3] Installing dependencies...
pip install -q ollama psutil GPUtil

echo.
echo [3/3] Running benchmarks on all 3 models...
echo.

REM Test all 3 models
python benchmarks\benchmark_ollama.py --model phi3:3.8b --test_name phi3_3.8b --output benchmarks\results

echo.
echo ----------------------------------------
python benchmarks\benchmark_ollama.py --model gemma2:2b --test_name gemma2_2b --output benchmarks\results

echo.
echo ----------------------------------------
python benchmarks\benchmark_ollama.py --model qwen2.5:3b --test_name qwen2.5_3b --output benchmarks\results

echo.
echo ========================================
echo   DONE! Check results in:
echo   benchmarks\results\
echo ========================================
pause
