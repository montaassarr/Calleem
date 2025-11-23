#!/bin/bash
# AI Receptionist - Production Mode Startup Script
# Builds and starts all containers in production mode

set -e

echo "🚀 AI Receptionist - Production Mode"
echo "====================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    echo "Please create .env from .env.new.example and configure it"
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating environment configuration..."
required_vars=(
    "MONGO_INITDB_ROOT_PASSWORD"
    "SECRET_KEY"
    "GROQ_API_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env || grep -q "^${var}=xxx" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing or invalid required environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please configure these in your .env file"
    exit 1
fi

echo -e "${GREEN}✓ Environment validation passed${NC}"
echo ""

echo "📋 Configuration:"
echo "  - Environment: Production"
echo "  - Hot Reload: Disabled"
echo "  - Workers: Multiple"
echo "  - Profile: prod"
echo ""

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker compose -f docker compose.new.yml --profile prod down 2>/dev/null || true
echo ""

# Build images with no cache for production
echo "🔨 Building production Docker images (this may take a while)..."
docker compose -f docker compose.new.yml --profile prod build --no-cache
echo ""

# Start containers in detached mode
echo "🚀 Starting containers in production mode..."
docker compose -f docker compose.new.yml --profile prod up -d
echo ""

# Wait for containers to be healthy
echo "⏳ Waiting for containers to be healthy..."
sleep 10

# Show container status
echo ""
echo "📊 Container Status:"
docker compose -f docker compose.new.yml --profile prod ps
echo ""

# Show setup logs
echo "📝 Setup Container Logs:"
docker compose -f docker compose.new.yml logs setup
echo ""

# Health check
echo "🏥 Health Checks:"
max_retries=30
retry_count=0

echo -n "  Backend API: "
while [ $retry_count -lt $max_retries ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo -e "${RED}✗ Failed to become healthy${NC}"
fi

echo -n "  Frontend: "
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        break
    fi
    retry_count=$((retry_count + 1))
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo -e "${RED}✗ Failed to become healthy${NC}"
fi

echo ""
echo -e "${GREEN}✅ Production environment started!${NC}"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "  View logs:        docker compose -f docker compose.new.yml --profile prod logs -f"
echo "  Stop containers:  ./stop.sh"
echo "  Restart:          docker compose -f docker compose.new.yml --profile prod restart"
echo ""
echo "⚠️  Production Notes:"
echo "  - Configure Traefik for HTTPS in production"
echo "  - Set up proper domain and SSL certificates"
echo "  - Configure firewall rules"
echo "  - Set up monitoring and logging"
echo ""
