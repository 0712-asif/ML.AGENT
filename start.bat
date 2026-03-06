@echo off

REM AutoML Platform Startup Script for Windows

echo 🤖 Starting AutoML Platform...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if pip is installed  
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "project\models" mkdir project\models
if not exist "project\datasets" mkdir project\datasets
if not exist "project\logs" mkdir project\logs  
if not exist "project\runs" mkdir project\runs

REM Start the server
echo 🚀 Starting AutoML Platform on http://localhost:8000
echo    - Dashboard: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd project
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

pause