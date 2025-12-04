#!/bin/bash

# AI Receptionist - Stop All Services

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Services...${NC}"
echo ""

pkill -f "uvicorn main:app" && echo -e "${GREEN}✅ Backend${NC}" || echo -e "⚠️  Backend not running"
pkill -f "next dev" && echo -e "${GREEN}✅ Frontend${NC}" || echo -e "⚠️  Frontend not running"
docker stop n8n 2>/dev/null && echo -e "${GREEN}✅ N8N${NC}" || echo -e "⚠️  N8N not running"

# Uncomment to stop MongoDB:
# sudo systemctl stop mongod && echo -e "${GREEN}✅ MongoDB${NC}"

rm -f .service_pids

echo ""
echo -e "${GREEN}✅ Done${NC}"
echo "Start: ./scripts/start_all.sh"
