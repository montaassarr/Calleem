#!/bin/bash
# AI Receptionist - Development Mode Startup Script
# Starts all containers with hot reload enabled

set -e

echo "🚀 AI Receptionist - Development Mode"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Warning: .env file not found${NC}"
    echo "Creating .env from .env.new.example..."
    cp .env.new.example .env
    echo -e "${RED}✗ Please configure your .env file with actual API keys before continuing${NC}"
    echo "Edit .env and fill in:"
    echo "  - GROQ_API_KEY"
    echo "  - OPENAI_API_KEY"
    echo "  - VAPI_API_KEY"
    echo "  - WHATSAPP_TOKEN"
    echo "  - SECRET_KEY"
    echo ""
    exit 1
fi

# Check if docker compose.new.yml exists
if [ ! -f "docker compose.new.yml" ]; then
    echo -e "${RED}✗ docker compose.new.yml not found${NC}"
    exit 1
fi

echo "📋 Configuration:"
echo "  - Environment: Development"
echo "  - Hot Reload: Enabled"
echo "  - Profile: dev"
echo ""

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker compose -f docker compose.new.yml --profile dev down 2>/dev/null || true
echo ""

# Build images
echo "🔨 Building Docker images..."
docker compose -f docker compose.new.yml --profile dev build
echo ""

# Start containers
echo "🚀 Starting containers..."
docker compose -f docker compose.new.yml --profile dev up -d
echo ""

# Wait a moment for containers to start
sleep 3

# Show container status
echo "📊 Container Status:"
docker compose -f docker compose.new.yml --profile dev ps
echo ""

# Show logs from setup container
echo "📝 Setup Container Logs:"
docker compose -f docker compose.new.yml logs setup
echo ""

# Health check
echo "🏥 Health Checks:"
echo -n "  Backend API: "
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⊘ Not ready yet (may take a moment)${NC}"
fi

echo -n "  Frontend: "
if curl -sf http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⊘ Not ready yet (may take a moment)${NC}"
fi

echo ""
echo -e "${GREEN}✅ Development environment started!${NC}"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  MongoDB:   mongodb://localhost:27017"
echo ""
echo "📝 Useful commands:"
echo "  View logs:        docker compose -f docker compose.new.yml --profile dev logs -f"
echo "  Stop containers:  ./stop.sh"
echo "  Restart:          docker compose -f docker compose.new.yml --profile dev restart"
echo ""
echo "💡 Hot reload is enabled - changes to code will auto-reload!"
echo ""
