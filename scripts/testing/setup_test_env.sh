#!/bin/bash

# Test Environment Setup Script
# =============================
# Prepares environment for Phase 1 testing

set -e

echo "🔧 Setting up test environment for Phase 1..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
    echo -e "${RED}❌ Python 3.8+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"
echo ""

# 2. Create/activate virtual environment
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# 3. Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q
cd ..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# 4. Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r tests/requirements.txt -q
echo -e "${GREEN}✅ Test dependencies installed${NC}"
echo ""

# 5. Check MongoDB
echo "🔍 Checking MongoDB..."
if nc -z localhost 27017 2>/dev/null; then
    echo -e "${GREEN}✅ MongoDB is running${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB not running. Starting via Docker...${NC}"
    docker-compose up -d mongodb
    sleep 5
    
    if nc -z localhost 27017 2>/dev/null; then
        echo -e "${GREEN}✅ MongoDB started${NC}"
    else
        echo -e "${RED}❌ Failed to start MongoDB${NC}"
        exit 1
    fi
fi
echo ""

# 6. Setup test database
echo "🗄️  Setting up test database..."
mongosh mongodb://localhost:27017/ai_receptionist_test --quiet --eval "
db.users.createIndex({ email: 1 }, { unique: true });
db.tenants.createIndex({ email: 1 }, { unique: true });
db.api_keys.createIndex({ tenant_id: 1, provider: 1 });
db.appointments.createIndex({ tenant_id: 1, start_time: 1 });
db.conversations.createIndex({ tenant_id: 1, created_at: -1 });
db.agents.createIndex({ tenant_id: 1 });
print('Test database indexes created');
"
echo -e "${GREEN}✅ Test database configured${NC}"
echo ""

# 7. Check/create .env file
echo "⚙️  Checking environment configuration..."
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    
    cat > backend/.env << EOF
# Application
APP_NAME="AI Receptionist"
LOG_LEVEL=INFO
FRONTEND_URL=http://localhost:3000

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_receptionist_test

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MASTER_KEY=$(openssl rand -hex 32)

# Platform API Keys (for testing - replace with real keys)
OPENAI_PLATFORM_KEY=your_platform_openai_key_here
GROQ_PLATFORM_KEY=your_platform_groq_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=REDACTED
N8N_WEBHOOK_URL=http://localhost:5678/webhook

# LiveKit (managed voice)
LIVEKIT_URL=https://your-livekit.example.com
LIVEKIT_API_KEY=REDACTED
LIVEKIT_API_SECRET=REDACTED
LIVEKIT_AGENT_NAME=Parker165
LIVEKIT_AGENT_QUEUE=default

# Testing
TESTING=true
EOF
    
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please update platform API keys in backend/.env${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi
echo ""

# 8. Verify backend can start
echo "🔍 Verifying backend configuration..."
cd backend
python3 -c "
import sys
try:
    from main import app
    print('Backend configuration valid')
    sys.exit(0)
except Exception as e:
    print(f'Backend configuration error: {e}')
    sys.exit(1)
" || {
    echo -e "${RED}❌ Backend configuration error${NC}"
    cd ..
    exit 1
}
cd ..
echo -e "${GREEN}✅ Backend configuration valid${NC}"
echo ""

# 9. Create logs directory
echo "📁 Creating logs directory..."
mkdir -p backend/logs
mkdir -p logs
echo -e "${GREEN}✅ Logs directory created${NC}"
echo ""

# 10. Summary
echo "=========================================="
echo "✅ Test Environment Setup Complete!"
echo "=========================================="
echo ""
echo "Environment ready for Phase 1 testing:"
echo "  ✅ Python $PYTHON_VERSION"
echo "  ✅ Virtual environment (venv)"
echo "  ✅ Backend dependencies installed"
echo "  ✅ Test dependencies installed"
echo "  ✅ MongoDB running on localhost:27017"
echo "  ✅ Test database configured"
echo "  ✅ Environment variables configured"
echo "  ✅ Backend configuration validated"
echo ""
echo "Next steps:"
echo "  1. Update platform API keys in backend/.env (if needed)"
echo "  2. Start backend: cd backend && uvicorn main:app --reload"
echo "  3. Run Phase 1 tests: ./scripts/testing/run_phase1_tests.sh"
echo ""
echo "Documentation:"
echo "  - docs/testing/TESTING_STRATEGY.md"
echo "  - docs/testing/PHASE1_EXECUTION_GUIDE.md"
echo "  - docs/testing/PHASE1_QUICKSTART.md"
echo ""
