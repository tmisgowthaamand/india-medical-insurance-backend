@echo off
echo ========================================
echo QUICK BACKEND TERMINAL FIX
echo ========================================

REM Change to backend directory
cd /d "c:\Users\Admin\CascadeProjects\india-medical-insurance-dashboard\backend"

echo Current directory: %CD%

REM Kill existing Python processes
echo Killing existing Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

REM Kill processes on ports 8000 and 8001
echo Killing processes on ports 8000 and 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a 2>nul

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment found, activating...
    call .venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Start the backend server
echo Starting backend server on port 8001...
echo Server will be available at: http://localhost:8001
echo API docs will be available at: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

pause
