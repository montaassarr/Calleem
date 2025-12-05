#!/bin/bash

# AI Receptionist - Start Script
# Consolidates all services into Docker Compose

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI Receptionist - Starting All Services (Docker)${NC}"
echo ""

# 1. Check/Create .env file
if [ ! -f ".env" ]; then
    if [ -f "backend/.env" ]; then
        echo -e "${YELLOW}⚠️  Root .env not found. Creating from backend/.env...${NC}"
        cp backend/.env .env
        echo -e "${GREEN}✅ Created .env${NC}"
    else
        echo -e "${RED}❌ backend/.env not found! Cannot configure services.${NC}"
        exit 1
    fi
fi

# Function to kill process on port
kill_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port in use. Killing process...${NC}"
        sudo kill -9 $(lsof -Pi :$port -sTCP:LISTEN -t) 2>/dev/null || true
        sleep 1
    fi
}

# 2. Stop existing containers and clean ports
echo -e "${BLUE}🛑 Stopping existing containers and cleaning ports...${NC}"
docker compose down --remove-orphans
kill_port 27017 # MongoDB
kill_port 5678  # N8N
kill_port 8000  # Backend
kill_port 3000  # Frontend
echo ""

# 3. Build and Start
echo -e "${BLUE}🏗️  Building and Starting services...${NC}"
docker compose up --build -d

# 4. Wait for services
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# 5. Show status
echo ""
echo "════════════════════════════════════════════"
echo -e "${GREEN}🎉 Services Started${NC}"
echo "════════════════════════════════════════════"
echo ""
echo "Frontend:     http://localhost:3000"
echo "Backend:      http://localhost:8000/docs"
echo "N8N:          http://localhost:5678"
echo "MongoDB:      localhost:27017"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop:      docker compose down"
echo ""
