#!/bin/bash

# Phase 1 Test Runner - Backend API & Tenant Isolation
# =====================================================
# Run all Phase 1 integration tests for Voice-First BYOK architecture

set -e  # Exit on error

echo "🧪 Phase 1: Backend API & Tenant Isolation Tests"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  uvicorn main:app --reload"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Check if MongoDB is running
echo "🔍 Checking if MongoDB is running..."
if ! nc -z localhost 27017 2>/dev/null; then
    echo -e "${RED}❌ MongoDB is not running!${NC}"
    echo "Please start MongoDB first:"
    echo "  docker-compose up -d mongodb"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB is running${NC}"
echo ""

# Set test environment variables
export TESTING=true
export JWT_SECRET_KEY="REDACTED"
export MONGODB_URL="mongodb://localhost:27017"
export DATABASE_NAME="ai_receptionist_test"

echo "🧹 Cleaning test database..."
mongosh mongodb://localhost:27017/ai_receptionist_test --quiet --eval "db.dropDatabase()" || true
echo -e "${GREEN}✅ Test database cleaned${NC}"
echo ""

# Install test dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r tests/requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "=========================================="
echo "Phase 1.1: Authentication & Authorization"
echo "=========================================="
pytest tests/integration/test_auth.py -v -s --tb=short || {
    echo -e "${RED}❌ Authentication tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Authentication tests passed${NC}"
echo ""

echo "=========================================="
echo "Phase 1.2: Tenant Isolation (CRITICAL) ⭐"
echo "=========================================="
pytest tests/integration/test_tenant_isolation.py -v -s --tb=short || {
    echo -e "${RED}❌ Tenant isolation tests FAILED - CRITICAL ISSUE!${NC}"
    exit 1
}
echo -e "${GREEN}✅✅✅ Tenant isolation tests passed (CRITICAL)${NC}"
echo ""

echo "=========================================="
echo "Phase 1.3: API Key Management"
echo "=========================================="
pytest tests/integration/test_api_keys.py -v -s --tb=short || {
    echo -e "${RED}❌ API key tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ API key tests passed${NC}"
echo ""

echo "=========================================="
echo "Phase 1.4: AI Proxy Service"
echo "=========================================="
pytest tests/integration/test_ai_proxy.py -v -s --tb=short || {
    echo -e "${RED}❌ AI Proxy tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ AI Proxy tests passed${NC}"
echo ""

echo "=========================================="
echo "Phase 1.5: Onboarding Wizard"
echo "=========================================="
pytest tests/integration/test_onboarding.py -v -s --tb=short || {
    echo -e "${RED}❌ Onboarding tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Onboarding tests passed${NC}"
echo ""

echo "=========================================="
echo "📊 Phase 1 Test Summary"
echo "=========================================="
echo -e "${GREEN}✅ All Phase 1 tests passed!${NC}"
echo ""
echo "Tests completed:"
echo "  ✅ Authentication & Authorization"
echo "  ✅ Tenant Isolation (CRITICAL)"
echo "  ✅ API Key Management"
echo "  ✅ AI Proxy Service (3-tier strategy)"
echo "  ✅ Onboarding Wizard"
echo ""
echo "🎉 Phase 1 Complete - Backend API & Tenant Isolation Verified!"
echo ""
echo "Next Steps:"
echo "  📞 Phase 2: Voice Provider Integration Tests"
echo "  🔄 Phase 3: End-to-End Workflow Tests"
echo "  ☁️  Phase 4: AWS Deployment Readiness"
echo ""

# Generate coverage report
echo "📊 Generating coverage report..."
pytest tests/integration/ --cov=backend --cov-report=html --cov-report=term-missing

echo ""
echo "Coverage report saved to: htmlcov/index.html"
echo "Open with: open htmlcov/index.html"
echo ""
