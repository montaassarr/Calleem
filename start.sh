#!/bin/bash

# AI Receptionist - Unified Start Script
# Supports both localhost and Docker modes
# Usage: 
#   ./start.sh              # Start in localhost mode
#   ./start.sh docker       # Start in Docker mode
#   ./start.sh docker [service]  # Start specific Docker service

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

MODE="${1:-localhost}"
SERVICE="${2:-}"

print_header() {
    echo ""
    echo "════════════════════════════════════════════"
    echo -e "${BLUE}🚀 AI Receptionist - Start Services${NC}"
    echo "════════════════════════════════════════════"
    echo ""
}

print_footer() {
    echo ""
    echo "════════════════════════════════════════════"
    echo -e "${GREEN}$1${NC}"
    echo "════════════════════════════════════════════"
    echo ""
}

check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

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

start_docker() {
    print_header
    echo -e "${BLUE}🐳 Docker Mode${NC}"
    echo ""
    
    if [ -n "$SERVICE" ]; then
        echo -e "${YELLOW}Starting service: $SERVICE${NC}"
        docker-compose up -d "$SERVICE"
        echo -e "${GREEN}✅ Service '$SERVICE' started${NC}"
    else
        echo -e "${YELLOW}Starting all services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✅ All services started${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${BLUE}📋 Service URLs:${NC}"
    echo "Frontend:     http://localhost:3000"
    echo "Backend:      http://localhost:8000"
    echo "API Docs:     http://localhost:8000/docs"
    echo "MongoDB:      mongodb://localhost:27017"
    echo ""
    echo -e "${YELLOW}View logs:${NC}"
    echo "  docker-compose logs -f                    # All services"
    echo "  docker-compose logs -f frontend           # Frontend only"
    echo "  docker-compose logs -f core-service       # Backend only"
    echo ""
    echo -e "${YELLOW}Stop:${NC} ./stop.sh docker"
    
    print_footer "🎉 Docker Services Running"
}

start_localhost() {
    print_header
    echo -e "${BLUE}💻 Localhost Mode${NC}"
    echo ""
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ Missing .env file in root directory${NC}"
        echo "Please create .env file with required environment variables"
        exit 1
    fi
    
    # 1. MongoDB
    echo -e "${BLUE}📦 Step 1/3: MongoDB${NC}"
    if systemctl is-active --quiet mongod 2>/dev/null; then
        echo -e "${GREEN}✅ MongoDB already running${NC}"
    elif sudo systemctl start mongod 2>/dev/null; then
        echo -e "${GREEN}✅ MongoDB started${NC}"
        sleep 2
    else
        echo -e "${YELLOW}⚠️  Could not start MongoDB via systemctl${NC}"
        echo -e "${YELLOW}   Please ensure MongoDB is running manually${NC}"
    fi
    echo ""
    
    # 2. Backend
    echo -e "${BLUE}🐍 Step 2/3: Backend API${NC}"
    if check_port 8000; then
        echo -e "${YELLOW}⚠️  Port 8000 in use, stopping existing process...${NC}"
        pkill -f "uvicorn main:app" 2>/dev/null || true
        sleep 2
    fi
    
    cd backend
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    mkdir -p ../logs
    
    echo -e "${YELLOW}⏳ Starting backend server...${NC}"
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "BACKEND_PID=$BACKEND_PID" > ../.service_pids
    
    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    cd ..
    wait_for_service "http://localhost:8000/docs" "Backend API"
    echo ""
    
    # 3. Frontend
    echo -e "${BLUE}⚛️  Step 3/3: Frontend${NC}"
    if check_port 3000; then
        echo -e "${YELLOW}⚠️  Port 3000 in use, stopping existing process...${NC}"
        pkill -f "next dev" 2>/dev/null || true
        sleep 2
    fi
    
    cd frontend_next
    
    # Check node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
        npm install
    fi
    
    mkdir -p ../logs
    
    echo -e "${YELLOW}⏳ Starting frontend server...${NC}"
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "FRONTEND_PID=$FRONTEND_PID" >> ../.service_pids
    
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    cd ..
    wait_for_service "http://localhost:3000" "Frontend"
    echo ""
    
    # Summary
    echo "════════════════════════════════════════════"
    echo -e "${GREEN}🎉 All Services Running${NC}"
    echo "════════════════════════════════════════════"
    echo ""
    echo -e "${BLUE}📋 Service URLs:${NC}"
    echo "Frontend:     http://localhost:3000"
    echo "Backend:      http://localhost:8000"
    echo "API Docs:     http://localhost:8000/docs"
    echo "MongoDB:      mongodb://localhost:27017"
    echo ""
    echo -e "${BLUE}📊 Process IDs:${NC}"
    echo "Backend:      $BACKEND_PID"
    echo "Frontend:     $FRONTEND_PID"
    echo ""
    echo -e "${BLUE}📄 Log Files:${NC}"
    echo "Backend:      tail -f logs/backend.log"
    echo "Frontend:     tail -f logs/frontend.log"
    echo ""
    echo -e "${YELLOW}Stop Services:${NC} ./stop.sh"
    echo "════════════════════════════════════════════"
    echo ""
    echo -e "${BLUE}📊 Monitoring logs (Ctrl+C to exit)${NC}"
    echo ""
    
    # Follow logs
    tail -f logs/backend.log logs/frontend.log 2>/dev/null
}

# Main execution
case "$MODE" in
    docker)
        start_docker
        ;;
    localhost|local)
        start_localhost
        ;;
    *)
        echo -e "${RED}❌ Invalid mode: $MODE${NC}"
        echo ""
        echo "Usage:"
        echo "  ./start.sh                    # Start in localhost mode"
        echo "  ./start.sh localhost          # Start in localhost mode"
        echo "  ./start.sh docker             # Start all Docker services"
        echo "  ./start.sh docker frontend    # Start specific Docker service"
        echo ""
        exit 1
        ;;
esac
