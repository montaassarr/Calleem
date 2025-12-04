#!/bin/bash

# AI Receptionist - Start All Services
# Starts: MongoDB, N8N, Backend, Frontend

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI Receptionist - Starting All Services${NC}"
echo ""

# Port checker
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Service waiter
wait_for_service() {
    local url=$1
    local name=$2
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for $name...${NC}"
    while [ $attempt -lt 30 ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    echo -e "${RED}❌ $name timeout${NC}"
    return 1
}

# 1. MongoDB
echo -e "${BLUE}📦 MongoDB...${NC}"
if systemctl is-active --quiet mongod 2>/dev/null; then
    echo -e "${GREEN}✅ Running${NC}"
elif sudo systemctl start mongod 2>/dev/null; then
    echo -e "${GREEN}✅ Started${NC}"
else
    echo -e "${YELLOW}⚠️  Check manually${NC}"
fi
echo ""

# 2. N8N
echo -e "${BLUE}🔧 N8N...${NC}"
if docker ps | grep -q "n8n"; then
    echo -e "${GREEN}✅ Running${NC}"
elif docker ps -a | grep -q "n8n"; then
    docker start n8n && echo -e "${GREEN}✅ Started${NC}"
else
    docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n && echo -e "${GREEN}✅ Created${NC}"
fi
echo ""

# 3. Backend
echo -e "${BLUE}🐍 Backend...${NC}"
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 in use, killing process...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null || true
    sleep 2
fi

cd backend

if [ ! -f ".env" ] && [ ! -f "../backend/.env" ]; then
    echo -e "${RED}❌ Missing backend/.env file${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating backend virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

export PYTHONPATH="$(pwd):$PYTHONPATH"

# Create logs directory if it doesn't exist
mkdir -p ../logs

echo -e "${YELLOW}⏳ Starting uvicorn...${NC}"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Started (PID: $BACKEND_PID)${NC}"
cd ..
wait_for_service "http://localhost:8000/docs" "Backend"
echo ""

# 4. Frontend
echo -e "${BLUE}⚛️  Frontend...${NC}"
if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 in use, killing process...${NC}"
    pkill -f "next dev" 2>/dev/null || true
    sleep 2
fi

cd frontend_next

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
fi

# Create logs directory if it doesn't exist
mkdir -p ../logs

echo -e "${YELLOW}⏳ Starting Next.js...${NC}"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Started (PID: $FRONTEND_PID)${NC}"
cd ..
wait_for_service "http://localhost:3000" "Frontend"
echo ""

# Summary
echo "════════════════════════════════════════════"
echo -e "${GREEN}🎉 All Services Running${NC}"
echo "════════════════════════════════════════════"
echo ""
echo "MongoDB:      mongodb://localhost:27017"
echo "N8N:          http://localhost:5678"
echo "Backend:      http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend:     http://localhost:3000"
echo ""
echo "Logs:         logs/backend.log | logs/frontend.log"
echo "Stop:         ./scripts/stop_all.sh"
echo ""
echo "════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📊 Monitoring logs (Ctrl+C to exit)${NC}"
echo ""

echo "BACKEND_PID=$BACKEND_PID" > .service_pids
echo "FRONTEND_PID=$FRONTEND_PID" >> .service_pids

tail -f logs/backend.log logs/frontend.log 2>/dev/null
