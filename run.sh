#!/bin/bash
# AlgoChat Pay - Linux/Mac Quick Start Script

echo "============================================================"
echo "         AlgoChat Pay - Campus Wallet on WhatsApp"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    echo ""
    echo "    cp .env.example .env"
    echo ""
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo ""

# Initialize database
echo "Initializing database..."
python -c "from backend.database import init_db; init_db()"
echo ""

# Start server
echo "============================================================"
echo "Starting AlgoChat Pay server..."
echo ""
echo "Server: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "WhatsApp Webhook: http://localhost:8000/webhook/whatsapp"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
