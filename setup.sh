#!/bin/bash

# AI Receptionist - Quick Start Script for Ubuntu
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "AI Receptionist - Quick Start"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Ubuntu/Debian
if [ ! -f /etc/debian_version ]; then
    echo -e "${RED}This script is designed for Ubuntu/Debian systems.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}Step 2: Installing Python 3.11...${NC}"
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

echo -e "${YELLOW}Step 3: Installing MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    sudo apt update
    sudo apt install -y mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
    echo -e "${GREEN}✓ MongoDB installed and started${NC}"
else
    echo -e "${GREEN}✓ MongoDB already installed${NC}"
fi

echo -e "${YELLOW}Step 4: Setting up Python virtual environment...${NC}"
cd backend
python3.11 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}Step 5: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}Step 6: Creating environment file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit backend/.env with your actual credentials!${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo -e "${YELLOW}Step 7: Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

echo -e "${YELLOW}Step 8: Initializing database...${NC}"
mongosh --eval "
use ai_barber_receptionist;
db.createCollection('appointments');
db.createCollection('conversations');
db.createCollection('services');
db.createCollection('users');
" > /dev/null 2>&1
echo -e "${GREEN}✓ Database initialized${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete! 🎉${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your credentials:"
echo "   - TWILIO_ACCOUNT_SID"
echo "   - TWILIO_AUTH_TOKEN"
echo "   - TWILIO_PHONE_NUMBER"
echo "   - GROQ_API_KEY"
echo ""
echo "2. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo ""
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For detailed setup instructions, see docs/setup_guide.md"
echo ""
