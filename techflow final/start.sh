#!/bin/bash

echo "TechFlow Issue Tracking System - Unix/Linux/Mac Startup"
echo "========================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager or https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create uploads directory
mkdir -p static/uploads

# Make run.py executable
chmod +x run.py

# Start the application
echo "🚀 Starting TechFlow Issue Tracking System..."
echo "Application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "========================================================"

python3 run.py
