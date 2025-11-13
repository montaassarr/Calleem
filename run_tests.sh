#!/bin/bash

# AI Receptionist - System Test Runner
# This script checks if the server is running and runs the test suite

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   AI Receptionist - Test Runner     ${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Check if server is running on port 8000
echo -e "${YELLOW}Checking if backend server is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend server is running${NC}\n"
else
    echo -e "${RED}✗ Backend server is NOT running${NC}"
    echo -e "${YELLOW}Starting backend server...${NC}"
    
    cd backend
    . venv/bin/activate
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/server.log 2>&1 &
    SERVER_PID=$!
    cd ..
    
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend server started successfully (PID: $SERVER_PID)${NC}\n"
    else
        echo -e "${RED}✗ Failed to start backend server${NC}"
        echo -e "${YELLOW}Check logs/server.log for details${NC}"
        exit 1
    fi
fi

# Check if ngrok is running
echo -e "${YELLOW}Checking if ngrok is running...${NC}"
if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)
    if [ -n "$NGROK_URL" ]; then
        echo -e "${GREEN}✓ ngrok is running${NC}"
        echo -e "${BLUE}  Public URL: $NGROK_URL${NC}\n"
    else
        echo -e "${YELLOW}⚠ ngrok is running but no tunnels found${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ ngrok is NOT running${NC}"
    echo -e "${YELLOW}  Start with: ngrok http 8000${NC}\n"
fi

# Run the Python test suite
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}      Running Test Suite...          ${NC}"
echo -e "${BLUE}======================================${NC}\n"

python3 test_system.py
TEST_RESULT=$?

echo -e "\n${BLUE}======================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed. See above for details.${NC}"
fi
echo -e "${BLUE}======================================${NC}\n"

exit $TEST_RESULT
