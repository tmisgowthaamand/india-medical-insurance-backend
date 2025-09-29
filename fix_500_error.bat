@echo off
echo 🚨 EMERGENCY 500 ERROR FIX
echo ========================
echo.
echo Running automated fix for Render service srv-d3b668ogjchc73f9ece0
echo.

cd /d "%~dp0"

echo 🔄 Starting emergency fix script...
python emergency_fix_500_error.py

echo.
echo 📋 Fix completed. Check the output above for results.
echo.
echo 🔧 If the fix failed, run this manual command:
echo    python quick_database_fix.py
echo.
pause
