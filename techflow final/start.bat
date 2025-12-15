@echo off
echo TechFlow Issue Tracking System - Windows Startup
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create uploads directory
if not exist "static\uploads" mkdir "static\uploads"

REM Start the application
echo Starting TechFlow Issue Tracking System...
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ================================================

python run.py

pause
