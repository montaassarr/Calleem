#!/bin/bash

# CallFlow AI - Quick Start Script
# This script sets up and starts the multi-tenant agent worker

set -e

echo "🚀 CallFlow AI - Multi-Tenant Agent Worker Setup"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.10 or higher required. You have: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env file with your LiveKit credentials"
    echo "   See README.md for instructions"
    exit 1
fi
echo "✅ Environment file found"
echo ""

# Check backend is running
echo "🔍 Checking if backend is running..."
BACKEND_URL=$(grep BACKEND_URL .env | cut -d '=' -f2)
if curl -s -f "$BACKEND_URL/docs" > /dev/null 2>&1; then
    echo "✅ Backend is running at $BACKEND_URL"
else
    echo "⚠️  Warning: Cannot reach backend at $BACKEND_URL"
    echo "   Make sure your backend is running:"
    echo "   cd .. && ./scripts/start_all.sh"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Start the agent worker
echo "🎙️  Starting CallFlow AI Agent Worker..."
echo "   Press Ctrl+C to stop"
echo ""
python main.py dev
