@echo off
REM Quick start script for benchmark testing
echo ========================================
echo   LLM Benchmark Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing dependencies...
pip install -r benchmarks\requirements.txt

echo.
echo [4/4] Ready to benchmark!
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo Option A: Download models first (recommended)
echo   python benchmarks\download_models.py
echo.
echo Option B: Use existing model
echo   python benchmarks\benchmark_inference.py --model path\to\model.gguf --n_gpu_layers 0 --test_name MyTest
echo.
echo Option C: Run full automated sweep
echo   python benchmarks\benchmark_sweep.py
echo.
echo ========================================
pause
