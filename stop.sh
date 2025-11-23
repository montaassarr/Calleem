#!/bin/bash
# AI Receptionist - Stop Script
# Gracefully stops all Docker containers

set -e

echo "🛑 AI Receptionist - Stopping Containers"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Determine which profile to stop
PROFILE="dev"
if [ "$1" == "prod" ] || [ "$1" == "production" ]; then
    PROFILE="prod"
fi

echo "Profile: $PROFILE"
echo ""

# Check if docker compose file exists
if [ ! -f "docker compose.new.yml" ]; then
    echo -e "${RED}✗ docker compose.new.yml not found${NC}"
    echo "Trying old docker compose.yml..."
    if [ -f "docker compose.yml" ]; then
        COMPOSE_FILE="docker compose.yml"
    else
        echo -e "${RED}✗ No docker compose file found${NC}"
        exit 1
    fi
else
    COMPOSE_FILE="docker compose.new.yml"
fi

# Stop containers
echo "🛑 Stopping containers..."
docker compose -f "$COMPOSE_FILE" --profile "$PROFILE" down

echo ""
echo -e "${GREEN}✅ Containers stopped successfully${NC}"
echo ""

# Ask if user wants to remove volumes
read -p "Do you want to remove volumes (this will delete all data)? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing volumes..."
    docker compose -f "$COMPOSE_FILE" --profile "$PROFILE" down -v
    echo -e "${GREEN}✓ Volumes removed${NC}"
fi

# Clean up orphaned containers
echo ""
echo "🧹 Cleaning up orphaned containers..."
docker container prune -f > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo ""
echo "Summary:"
echo "  - All containers stopped"
echo "  - Network removed"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - Volumes removed (data deleted)"
else
    echo "  - Volumes preserved (data intact)"
fi
echo ""
