#!/bin/bash

# AI Receptionist - Virtual Environment Setup Script
# This script creates and configures the Python virtual environment

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐍 Setting up Python Virtual Environment${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python ${PYTHON_VERSION}${NC}"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created at .venv${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ Pip upgraded${NC}"
echo ""

# Install backend dependencies
if [ -f "backend/requirements.txt" ]; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r backend/requirements.txt --quiet
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "${RED}❌ backend/requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Verify critical packages
echo -e "${YELLOW}Verifying critical packages...${NC}"
MISSING_PACKAGES=()

python -c "import fastapi" 2>/dev/null || MISSING_PACKAGES+=("fastapi")
python -c "import uvicorn" 2>/dev/null || MISSING_PACKAGES+=("uvicorn")
python -c "import motor" 2>/dev/null || MISSING_PACKAGES+=("motor")
python -c "import pymongo" 2>/dev/null || MISSING_PACKAGES+=("pymongo")
python -c "import groq" 2>/dev/null || MISSING_PACKAGES+=("groq")

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All critical packages verified${NC}"
else
    echo -e "${RED}❌ Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    exit 1
fi
echo ""

# Show installed packages count
PACKAGE_COUNT=$(pip list 2>/dev/null | wc -l)
echo -e "${BLUE}📦 Total packages installed: ${PACKAGE_COUNT}${NC}"
echo ""

echo -e "${GREEN}✅ Virtual environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}To activate the virtual environment manually, run:${NC}"
echo -e "  ${BLUE}source .venv/bin/activate${NC}"
echo ""
echo -e "${YELLOW}To start the application, run:${NC}"
echo -e "  ${BLUE}./start.sh${NC}"
echo ""
