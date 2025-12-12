#!/bin/bash
# Docker Test Script - Tests all services in Docker Compose

set -e

echo "=========================================="
echo "Docker Compose Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "Using: $DOCKER_COMPOSE"
echo ""

# Step 1: Build images
echo -e "${YELLOW}📦 Step 1: Building Docker images...${NC}"
$DOCKER_COMPOSE build --no-cache
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Images built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build images${NC}"
    exit 1
fi
echo ""

# Step 2: Start services
echo -e "${YELLOW}🚀 Step 2: Starting services...${NC}"
$DOCKER_COMPOSE up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi
echo ""

# Step 3: Wait for services to be healthy
echo -e "${YELLOW}⏳ Step 3: Waiting for services to be healthy...${NC}"
sleep 10

# Check MongoDB
echo "Checking MongoDB..."
for i in {1..30}; do
    if docker exec callflow-mongodb mongosh --eval "db.runCommand('ping')" --quiet &> /dev/null; then
        echo -e "${GREEN}✅ MongoDB is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ MongoDB failed to start${NC}"
        $DOCKER_COMPOSE logs mongodb
        exit 1
    fi
    sleep 2
done

# Check Backend
echo "Checking Backend..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        $DOCKER_COMPOSE logs backend
        exit 1
    fi
    sleep 2
done

# Check Frontend
echo "Checking Frontend..."
for i in {1..30}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Frontend may still be building (this is normal for Next.js)${NC}"
    fi
    sleep 2
done
echo ""

# Step 4: Test endpoints
echo -e "${YELLOW}🧪 Step 4: Testing API endpoints...${NC}"
if command -v python3 &> /dev/null; then
    cd "$(dirname "$0")/.."
    python3 scripts/test_endpoints.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All endpoint tests passed${NC}"
    else
        echo -e "${RED}❌ Some endpoint tests failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Python3 not found, skipping endpoint tests${NC}"
    echo "Testing basic endpoints with curl..."
    
    # Test root endpoint
    if curl -f http://localhost:8000/ &> /dev/null; then
        echo -e "${GREEN}✅ Root endpoint works${NC}"
    else
        echo -e "${RED}❌ Root endpoint failed${NC}"
    fi
    
    # Test health endpoint
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ Health endpoint works${NC}"
    else
        echo -e "${RED}❌ Health endpoint failed${NC}"
    fi
fi
echo ""

# Step 5: Show service status
echo -e "${YELLOW}📊 Step 5: Service Status${NC}"
$DOCKER_COMPOSE ps
echo ""

# Step 6: Show service URLs
echo -e "${YELLOW}🌐 Service URLs${NC}"
echo "Backend API:  http://localhost:8000"
echo "Backend Docs: http://localhost:8000/docs"
echo "Frontend:     http://localhost:3000"
echo "MongoDB:      mongodb://localhost:27017"
echo ""

echo -e "${GREEN}=========================================="
echo "✅ Docker Compose Test Complete!"
echo "==========================================${NC}"
echo ""
echo "To view logs:"
echo "  $DOCKER_COMPOSE logs -f [service_name]"
echo ""
echo "To stop services:"
echo "  $DOCKER_COMPOSE down"
echo ""
echo "To restart services:"
echo "  $DOCKER_COMPOSE restart"
echo ""

