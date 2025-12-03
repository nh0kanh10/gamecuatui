@echo off
pushd "%~dp0"
echo Testing Gemini Models...
python test_gemini_models.py
pause
popd

