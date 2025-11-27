#!/bin/bash

# AI Receptionist - Start All Services
echo "🚀 Starting AI Receptionist..."
echo ""

# Kill any existing ngrok processes
pkill -f ngrok 2>/dev/null

# Fix log file permissions if needed
if [ -f backend/logs/app.log ]; then
    if [ ! -w backend/logs/app.log ]; then
        echo "⚠️  Log file has wrong permissions. Removing old log file..."
        rm -f backend/logs/app.log 2>/dev/null || sudo rm -f backend/logs/app.log
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p backend/logs

# Start Backend
echo "📦 Starting Backend..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 8000 &
NGROK_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Services:"
echo "   - Backend:  http://localhost:8000"
echo "   - Frontend: http://localhost:5173"
echo "   - Ngrok:    Check terminal for public URL"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
