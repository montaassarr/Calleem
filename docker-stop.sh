#!/bin/bash

# AI Receptionist - Docker Stop Script
# This script stops all Docker services

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping AI Receptionist services...${NC}"
echo ""

# Stop and remove containers
docker compose down

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
echo "💡 To remove volumes (database data), run:"
echo "   docker compose down -v"
echo ""
echo "🔄 To start services again, run:"
echo "   ./docker-start.sh"
