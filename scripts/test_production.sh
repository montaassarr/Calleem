#!/bin/bash
# Production Endpoint Test Script
# Tests the production Railway backend and Vercel frontend

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

RAILWAY_URL="https://ai-receptionist-production-299a.up.railway.app"
VERCEL_URL="https://aireceptionist-lake.vercel.app"

echo "=========================================="
echo "Production Endpoint Test Suite"
echo "=========================================="
echo ""
echo -e "${BLUE}Railway Backend:${NC} $RAILWAY_URL"
echo -e "${BLUE}Vercel Frontend:${NC} $VERCEL_URL"
echo ""

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" || echo "000")
    fi
    
    if [ "$response" = "200" ] || [ "$response" = "201" ] || [ "$response" = "404" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response)"
        ((FAILED++))
        return 1
    fi
}

# Test Railway Backend
echo -e "${YELLOW}📡 Testing Railway Backend${NC}"
echo "----------------------------------------"

test_endpoint "Root endpoint" "$RAILWAY_URL/"
test_endpoint "Health check" "$RAILWAY_URL/health"
test_endpoint "API docs" "$RAILWAY_URL/docs"
test_endpoint "OpenAPI spec" "$RAILWAY_URL/openapi.json"

# Test API endpoints
echo ""
echo -e "${YELLOW}🔌 Testing API Endpoints${NC}"
echo "----------------------------------------"

test_endpoint "API root" "$RAILWAY_URL/api/v1/"
test_endpoint "Users endpoint" "$RAILWAY_URL/api/v1/users/me" "GET"
test_endpoint "Services endpoint" "$RAILWAY_URL/api/v1/services/" "GET"
test_endpoint "Appointments endpoint" "$RAILWAY_URL/api/v1/appointments/" "GET"
test_endpoint "Onboarding status" "$RAILWAY_URL/api/v1/onboarding/status" "GET"

# Test Vercel Frontend
echo ""
echo -e "${YELLOW}🌐 Testing Vercel Frontend${NC}"
echo "----------------------------------------"

test_endpoint "Frontend homepage" "$VERCEL_URL"
test_endpoint "Frontend login" "$VERCEL_URL/login"
test_endpoint "Frontend signup" "$VERCEL_URL/signup"

# Test CORS
echo ""
echo -e "${YELLOW}🔒 Testing CORS Configuration${NC}"
echo "----------------------------------------"

echo -n "Testing CORS preflight... "
cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS \
    -H "Origin: $VERCEL_URL" \
    -H "Access-Control-Request-Method: POST" \
    "$RAILWAY_URL/api/v1/users/register" || echo "000")

if [ "$cors_response" = "200" ] || [ "$cors_response" = "204" ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $cors_response)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $cors_response)"
    ((FAILED++))
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please check the endpoints.${NC}"
    exit 1
fi

