#!/bin/bash

# AI Receptionist - Docker Start Script
# This script starts all services using Docker Compose

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Starting AI Receptionist with Docker..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with your configuration.${NC}"
    echo -e "${YELLOW}You can copy from .env.example if available.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker and try again.${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${BLUE}Stopping existing containers...${NC}"
docker compose down 2>/dev/null || true
echo ""

# Build images (with cache)
echo -e "${BLUE}Building Docker images...${NC}"
docker compose build
echo ""

# Start services
echo -e "${BLUE}Starting services...${NC}"
docker compose up -d
echo ""

# Wait for services to be healthy
echo -e "${BLUE}Waiting for services to be ready...${NC}"
echo -e "${YELLOW}This may take a minute...${NC}"
echo ""

# Function to check service health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker compose ps | grep "$service" | grep -q "healthy\|Up"; then
            echo -e "${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}❌ $service failed to start${NC}"
    return 1
}

# Check each service
check_health "mongodb"
check_health "backend"
check_health "frontend"

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 AI Receptionist is running!${NC}"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   MongoDB:      localhost:27017"
echo ""
echo "🔐 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 View logs:"
echo "   All services:     docker compose logs -f"
echo "   Backend only:     docker compose logs -f backend"
echo "   Frontend only:    docker compose logs -f frontend"
echo ""
echo "🛑 To stop services:"
echo "   docker compose down"
echo ""
echo "🔄 To restart services:"
echo "   docker compose restart"
echo ""
echo "═══════════════════════════════════════════════════════"
