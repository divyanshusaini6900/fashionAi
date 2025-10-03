@echo off
echo ========================================
echo Fashion AI API Server Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    echo.
    pause
    exit /b 1
)

REM Install/update dependencies
echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo Starting Fashion AI API Server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

