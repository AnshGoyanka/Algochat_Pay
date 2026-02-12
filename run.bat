@echo off
REM AlgoChat Pay - Windows Quick Start Script

echo ============================================================
echo          AlgoChat Pay - Campus Wallet on WhatsApp
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it
    echo.
    echo    copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo.

REM Initialize database
echo Initializing database...
python -c "from backend.database import init_db; init_db()"
echo.

REM Start server
echo ============================================================
echo Starting AlgoChat Pay server...
echo.
echo Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo WhatsApp Webhook: http://localhost:8000/webhook/whatsapp
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
