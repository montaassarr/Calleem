#!/bin/bash

# AI Receptionist - Complete Startup Script
# Starts all services: MongoDB, N8N, Backend, Frontend

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AI Receptionist - Starting All Services${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for $name to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}❌ $name failed to start${NC}"
    return 1
}

# 1. Check/Start MongoDB
echo -e "${BLUE}📦 Checking MongoDB...${NC}"
if systemctl is-active --quiet mongod 2>/dev/null; then
    echo -e "${GREEN}✅ MongoDB is already running${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB is not running. Attempting to start...${NC}"
    if sudo systemctl start mongod 2>/dev/null; then
        echo -e "${GREEN}✅ MongoDB started successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not start MongoDB via systemd. It may already be running or not installed.${NC}"
    fi
fi
echo ""

# 2. Check/Start N8N
echo -e "${BLUE}🔧 Checking N8N...${NC}"
if docker ps | grep -q "n8n"; then
    echo -e "${GREEN}✅ N8N container is already running${NC}"
else
    echo -e "${YELLOW}⚠️  N8N is not running. Starting...${NC}"
    
    # Check if container exists but is stopped
    if docker ps -a | grep -q "n8n"; then
        echo -e "${YELLOW}Starting existing N8N container...${NC}"
        docker start n8n
    else
        echo -e "${YELLOW}Creating new N8N container...${NC}"
        docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
    fi
    
    echo -e "${GREEN}✅ N8N started${NC}"
fi
echo ""

# Start backend
echo -e "${BLUE}🐍 Starting Backend...${NC}"

# Check if backend is already running
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Stopping existing backend...${NC}"
    pkill -f "uvicorn main:app" || true
    sleep 2
fi

cd backend

# Check for .env file
if [ ! -f "../.env" ]; then
    echo -e "${RED}❌ .env file not found in root directory!${NC}"
    echo -e "${YELLOW}Please create .env file with required configuration${NC}"
    exit 1
fi

# Load environment variables from root .env
echo -e "${YELLOW}Loading environment variables from .env...${NC}"
export $(grep -v '^#' ../.env | xargs)

# Start backend
echo -e "${YELLOW}Starting backend server...${NC}"
export PYTHONPATH="$(pwd):$PYTHONPATH"
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
cd ..
echo ""

# Wait for backend to be ready
wait_for_service "http://localhost:8000/health" "Backend"
echo ""

# 4. Start Frontend
echo -e "${BLUE}⚛️  Starting Frontend...${NC}"

# Check if frontend is already running
if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Stopping existing frontend...${NC}"
    pkill -f "next dev" || true
    sleep 2
fi

cd frontend_next

# Check for node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

# Start frontend
echo -e "${YELLOW}Starting frontend server...${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
cd ..
echo ""

# Wait for frontend to be ready
wait_for_service "http://localhost:3000" "Frontend"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 All Services Started Successfully!${NC}"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📍 Service URLs:"
echo "   MongoDB:      mongodb://localhost:27017"
echo "   N8N:          http://localhost:5678"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:3000"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo "   N8N:      docker logs n8n"
echo ""
echo "🛑 To stop services:"
echo "   Backend:  kill $BACKEND_PID"
echo "   Frontend: kill $FRONTEND_PID"
echo "   N8N:      docker stop n8n"
echo "   MongoDB:  sudo systemctl stop mongod"
echo ""
echo "   Or run: ./stop_all.sh"
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✨ Ready to test multi-tenant API keys!${NC}"
echo -e "${YELLOW}👉 Go to: http://localhost:3000/dashboard/settings/integrations${NC}"
echo ""

# Keep script running to show logs
echo -e "${BLUE}📊 Monitoring services... (Press Ctrl+C to exit)${NC}"
echo ""

# Save PIDs for stop script
echo "BACKEND_PID=$BACKEND_PID" > .service_pids
echo "FRONTEND_PID=$FRONTEND_PID" >> .service_pids

# Tail logs
tail -f logs/backend.log logs/frontend.log 2>/dev/null
