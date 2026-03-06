#!/bin/bash

# AutoML Platform Startup Script

echo "🤖 Starting AutoML Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p project/models
mkdir -p project/datasets  
mkdir -p project/logs
mkdir -p project/runs

# Start the server
echo "🚀 Starting AutoML Platform on http://localhost:8000"
echo "   - Dashboard: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd project
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload