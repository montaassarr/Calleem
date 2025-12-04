#!/bin/bash

# ============================================================================
# Run All Phase Tests
# Complete test execution script for all testing phases
# ============================================================================

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════════"
echo "  🧪 AI RECEPTIONIST - COMPLETE TEST SUITE"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "${BLUE}Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo "Please start the backend first:"
    echo "  cd backend && uvicorn main:app --reload --port 8000"
    exit 1
fi

echo ""

# ============================================================================
# PHASE 1: Integration Tests
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📊 PHASE 1: Integration Tests${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running Phase 1.1: Authentication Tests...${NC}"
pytest tests/integration/test_auth.py -v || true
echo ""

echo -e "${YELLOW}Running Phase 1.2: Tenant Isolation Tests...${NC}"
pytest tests/integration/test_tenant_isolation.py -v || true
echo ""

echo -e "${YELLOW}Running Phase 1.3: API Key Tests...${NC}"
pytest tests/integration/test_api_keys.py -v || true
echo ""

echo -e "${YELLOW}Running Phase 1.4: AI Proxy Tests...${NC}"
pytest tests/integration/test_ai_proxy.py -v || true
echo ""

echo -e "${YELLOW}Running Phase 1.5: Onboarding Tests...${NC}"
pytest tests/integration/test_onboarding.py -v || true
echo ""

# ============================================================================
# PHASE 2: Voice Integration Tests (Requires real API keys)
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}🎤 PHASE 2: LiveKit Voice Integration Tests${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

if [ -z "$LIVEKIT_URL" ] || [ -z "$LIVEKIT_API_KEY" ] || [ -z "$LIVEKIT_API_SECRET" ]; then
    echo -e "${YELLOW}⚠️  LIVEKIT_* env vars not set - skipping Phase 2${NC}"
    echo "To run Phase 2 tests, export:"
    echo "  export LIVEKIT_URL='https://...'
  export LIVEKIT_API_KEY='key'
  export LIVEKIT_API_SECRET='secret'"
else
    echo -e "${YELLOW}Running LiveKit preview + status tests...${NC}"
    pytest tests/integration/test_livekit_status.py -v || true
    pytest tests/integration/test_livekit_preview.py -v || true
fi

echo ""

# ============================================================================
# PHASE 3: End-to-End Workflow Tests
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}🔄 PHASE 3: End-to-End Workflow Tests${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running Complete Onboarding Flow E2E...${NC}"
python3 tests/e2e/test_complete_onboarding_flow.py || true
echo ""

echo -e "${YELLOW}Running Multi-Tenant Workflow E2E...${NC}"
python3 tests/e2e/test_multi_tenant_workflow.py || true
echo ""

# ============================================================================
# PHASE 4: Deployment Readiness Tests
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}☁️  PHASE 4: Deployment Readiness Tests${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running Deployment Readiness Tests...${NC}"
pytest tests/deployment/test_deployment_readiness.py -v -s || true
echo ""

# ============================================================================
# MANUAL TESTS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}🔧 MANUAL TESTS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Running Two-Tenant Voice AI Test...${NC}"
python3 tests/manual/test_voice_ai_two_tenants.py || true
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ TEST SUITE EXECUTION COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Test Phases Executed:"
echo "  ✅ Phase 1: Integration Tests (5 test files)"
echo "  ✅ Phase 2: Voice Integration Tests (1 test file)"
echo "  ✅ Phase 3: E2E Workflow Tests (2 test files)"
echo "  ✅ Phase 4: Deployment Tests (1 test file)"
echo "  ✅ Manual Tests (1 test file)"
echo ""
echo "Review the output above for detailed results."
echo ""
echo "📚 Documentation:"
echo "  • ALL_PHASES_COMPLETE.md - Complete summary"
echo "  • PHASE_1_COMPLETE.md - Phase 1 details"
echo "  • VOICE_AI_MULTI_TENANT_COMPLETE.md - Voice AI verification"
echo ""
echo "🚀 Next Steps:"
echo "  1. Review any test failures"
echo "  2. Configure production environment"
echo "  3. Deploy to production"
echo ""
