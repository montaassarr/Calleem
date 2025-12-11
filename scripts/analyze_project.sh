#!/bin/bash

# Project Analysis & Health Check Script
# Run this from anywhere (it auto-detects root)

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend_next"
AGENT_DIR="$PROJECT_ROOT/livekit-agent-worker"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}      AI RECEPTIONIST - HEALTH REPORT       ${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Root: $PROJECT_ROOT"
echo "Date: $(date)"
echo ""

# 1. STRUCTURAL INTEGRITY
echo -e "${BLUE}--- [1] Structural Integrity ---${NC}"
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ Found: $(basename "$1")${NC}"
    else
        echo -e "${RED}❌ Missing: $(basename "$1")${NC}"
    fi
}
check_dir "$BACKEND_DIR"
check_dir "$FRONTEND_DIR"
check_dir "$AGENT_DIR"
check_dir "$PROJECT_ROOT/scripts"
check_dir "$PROJECT_ROOT/docs/archive"
echo ""

# 2. FILE STATS
echo -e "${BLUE}--- [2] Cleanliness Check ---${NC}"
ROOT_FILES=$(find "$PROJECT_ROOT" -maxdepth 1 -type f | wc -l)
echo "Files in root: $ROOT_FILES"
if [ "$ROOT_FILES" -lt 10 ]; then
    echo -e "${GREEN}✅ Root is clean.${NC}"
else
    echo -e "${RED}⚠️  Root contains $ROOT_FILES files. Consider moving them.${NC}"
fi
echo ""

# 3. SERVICE STATUS (Port Checks)
echo -e "${BLUE}--- [3] Service Status (Ports) ---${NC}"
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Port $1 ($2) is OPEN${NC}"
    else
        echo -e "${RED}🔴 Port $1 ($2) is CLOSED${NC}"
    fi
}
check_port 3000 "Frontend"
check_port 8000 "Backend"
check_port 5678 "N8N"
check_port 27017 "MongoDB"
echo ""

# 4. ENDPOINT DISCOVERY
echo -e "${BLUE}--- [4] Key Endpoints (Backend) ---${NC}"
if [ -d "$BACKEND_DIR" ]; then
    echo "Scanning routers..."
    # Extract router paths explicitly
    grep -r 'router = APIRouter' "$BACKEND_DIR" | while read -r line; do
        FILE=$(echo "$line" | cut -d: -f1)
        PREFIX=$(grep 'prefix=' "$FILE" | cut -d'"' -f2 | cut -d"'" -f2)
        echo " - Router in $(basename "$FILE"): Prefix '$PREFIX'"
    done
else
    echo "Backend not found, cannot scan endpoints."
fi

echo ""
echo -e "${BLUE}--- Analysis Complete ---${NC}"
exit 0
