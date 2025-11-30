#!/bin/bash

# AI Receptionist - Stop All Services Script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping All AI Receptionist Services${NC}"
echo ""

# Stop Backend
echo -e "${YELLOW}Stopping Backend...${NC}"
pkill -f "uvicorn main:app" && echo -e "${GREEN}✅ Backend stopped${NC}" || echo -e "${YELLOW}⚠️  Backend not running${NC}"

# Stop Frontend
echo -e "${YELLOW}Stopping Frontend...${NC}"
pkill -f "next dev" && echo -e "${GREEN}✅ Frontend stopped${NC}" || echo -e "${YELLOW}⚠️  Frontend not running${NC}"

# Stop N8N
echo -e "${YELLOW}Stopping N8N...${NC}"
docker stop n8n 2>/dev/null && echo -e "${GREEN}✅ N8N stopped${NC}" || echo -e "${YELLOW}⚠️  N8N not running${NC}"

# Optionally stop MongoDB (commented out by default)
# echo -e "${YELLOW}Stopping MongoDB...${NC}"
# sudo systemctl stop mongod && echo -e "${GREEN}✅ MongoDB stopped${NC}" || echo -e "${YELLOW}⚠️  MongoDB not running${NC}"

# Clean up PID file
rm -f .service_pids

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
echo "To start services again, run: ./start_all_services.sh"
