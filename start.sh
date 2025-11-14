#!/bin/bash

# AI Receptionist - Quick Start Script
# This script starts all necessary services

echo "🚀 Starting AI Receptionist System..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if MongoDB is running
echo -e "${BLUE}Checking MongoDB...${NC}"
if systemctl is-active --quiet mongod; then
    echo -e "${GREEN}✅ MongoDB is running${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB is not running. Starting it...${NC}"
    sudo systemctl start mongod
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ MongoDB started successfully${NC}"
    else
        echo -e "${YELLOW}❌ Failed to start MongoDB. Please start it manually.${NC}"
        exit 1
    fi
fi
echo ""

# Start Backend
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend
echo -e "${GREEN}✅ Backend will start at http://localhost:8000${NC}"
echo -e "${YELLOW}📝 API Docs: http://localhost:8000/docs${NC}"
echo ""

# Start backend in background with PYTHONPATH
export PYTHONPATH="/home/montassar/Desktop/ai_receptionist/backend:$PYTHONPATH"
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Wait a bit for backend to start
sleep 3

# Start Frontend
echo -e "${BLUE}Starting Frontend Dashboard...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Frontend will start at http://localhost:5173${NC}"
echo -e "${YELLOW}📝 Login: admin / admin123${NC}"
echo ""

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 AI Receptionist System is running!${NC}"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📍 Service URLs:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:5173"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: Check terminal output"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or press Ctrl+C in this terminal"
echo ""
echo "═══════════════════════════════════════════════════════"

# Keep script running
wait
