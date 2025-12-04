#!/bin/bash

# AI Receptionist - Unified Stop Script
# Supports both localhost and Docker modes
# Usage: 
#   ./stop.sh              # Stop localhost services
#   ./stop.sh docker       # Stop Docker services
#   ./stop.sh docker [service]  # Stop specific Docker service

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
    echo -e "${YELLOW}🛑 AI Receptionist - Stop Services${NC}"
    echo "════════════════════════════════════════════"
    echo ""
}

stop_docker() {
    print_header
    echo -e "${BLUE}🐳 Docker Mode${NC}"
    echo ""
    
    if [ -n "$SERVICE" ]; then
        echo -e "${YELLOW}Stopping service: $SERVICE${NC}"
        docker-compose stop "$SERVICE"
        echo -e "${GREEN}✅ Service '$SERVICE' stopped${NC}"
    else
        echo -e "${YELLOW}Stopping all Docker services...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ All Docker services stopped${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Container Status:${NC}"
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}✅ Done${NC}"
    echo -e "${YELLOW}Start again:${NC} ./start.sh docker"
    echo ""
}

stop_localhost() {
    print_header
    echo -e "${BLUE}💻 Localhost Mode${NC}"
    echo ""
    
    STOPPED=0
    
    # Stop Frontend
    echo -e "${YELLOW}Stopping Frontend...${NC}"
    if pkill -f "next dev" 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend stopped${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "${BLUE}ℹ️  Frontend not running${NC}"
    fi
    
    # Stop Backend
    echo -e "${YELLOW}Stopping Backend...${NC}"
    if pkill -f "uvicorn main:app" 2>/dev/null; then
        echo -e "${GREEN}✅ Backend stopped${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "${BLUE}ℹ️  Backend not running${NC}"
    fi
    
    # Stop N8N (Docker container)
    echo -e "${YELLOW}Stopping N8N...${NC}"
    if docker stop n8n 2>/dev/null; then
        echo -e "${GREEN}✅ N8N stopped${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "${BLUE}ℹ️  N8N not running${NC}"
    fi
    
    # MongoDB (optional - usually keep running)
    echo -e "${YELLOW}MongoDB Status...${NC}"
    if systemctl is-active --quiet mongod 2>/dev/null; then
        echo -e "${BLUE}ℹ️  MongoDB still running (not stopped by default)${NC}"
        echo -e "${YELLOW}   To stop: sudo systemctl stop mongod${NC}"
    else
        echo -e "${BLUE}ℹ️  MongoDB not running${NC}"
    fi
    
    # Clean up PID file
    if [ -f ".service_pids" ]; then
        rm -f .service_pids
        echo ""
        echo -e "${GREEN}✅ Cleaned up process tracking${NC}"
    fi
    
    echo ""
    echo "════════════════════════════════════════════"
    if [ $STOPPED -gt 0 ]; then
        echo -e "${GREEN}✅ Stopped $STOPPED service(s)${NC}"
    else
        echo -e "${BLUE}ℹ️  No services were running${NC}"
    fi
    echo "════════════════════════════════════════════"
    echo ""
    echo -e "${YELLOW}Start again:${NC} ./start.sh"
    echo ""
}

stop_all() {
    print_header
    echo -e "${RED}⚠️  Stopping ALL services (localhost + Docker)${NC}"
    echo ""
    
    # Stop localhost services
    echo -e "${BLUE}Localhost services:${NC}"
    pkill -f "next dev" 2>/dev/null && echo -e "${GREEN}✅ Frontend${NC}" || echo -e "${BLUE}ℹ️  Frontend not running${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null && echo -e "${GREEN}✅ Backend${NC}" || echo -e "${BLUE}ℹ️  Backend not running${NC}"
    
    echo ""
    echo -e "${BLUE}Docker services:${NC}"
    docker-compose down 2>/dev/null && echo -e "${GREEN}✅ Docker services${NC}" || echo -e "${BLUE}ℹ️  Docker not running${NC}"
    docker stop n8n 2>/dev/null && echo -e "${GREEN}✅ N8N${NC}" || echo -e "${BLUE}ℹ️  N8N not running${NC}"
    
    # Clean up
    rm -f .service_pids
    
    echo ""
    echo -e "${GREEN}✅ All services stopped${NC}"
    echo ""
}

# Main execution
case "$MODE" in
    docker)
        stop_docker
        ;;
    localhost|local)
        stop_localhost
        ;;
    all)
        stop_all
        ;;
    *)
        echo -e "${RED}❌ Invalid mode: $MODE${NC}"
        echo ""
        echo "Usage:"
        echo "  ./stop.sh                     # Stop localhost services"
        echo "  ./stop.sh localhost           # Stop localhost services"
        echo "  ./stop.sh docker              # Stop all Docker services"
        echo "  ./stop.sh docker frontend     # Stop specific Docker service"
        echo "  ./stop.sh all                 # Stop everything (localhost + Docker)"
        echo ""
        exit 1
        ;;
esac
