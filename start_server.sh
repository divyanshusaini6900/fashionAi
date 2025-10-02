#!/bin/bash

echo "========================================"
echo "Fashion AI API Server Startup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and add your API keys."
    echo ""
    read -p "Press enter to exit..."
    exit 1
fi

# Install/update dependencies
echo ""
echo "Checking dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "========================================"
echo "Starting Fashion AI API Server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

