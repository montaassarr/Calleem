#!/bin/bash

# AI Receptionist - Authentication Test Script
# Tests login and registration endpoints

echo "🧪 Testing AI Receptionist Authentication..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend Health Check
echo "1️⃣ Testing backend health..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend is not responding${NC}"
    exit 1
fi
echo ""

# Test 2: Login with admin credentials
echo "2️⃣ Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/users/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login successful${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
    echo -e "${YELLOW}Token (first 50 chars): ${TOKEN:0:50}...${NC}"
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Get current user info with token
echo "3️⃣ Testing authenticated endpoint (GET /users/me)..."
USER_INFO=$(curl -s http://localhost:8000/api/v1/users/me \
    -H "Authorization: Bearer $TOKEN")

if echo "$USER_INFO" | grep -q "admin"; then
    echo -e "${GREEN}✅ Authenticated request successful${NC}"
    echo "User: $(echo "$USER_INFO" | grep -o '"username":"[^"]*' | sed 's/"username":"//')"
    echo "Email: $(echo "$USER_INFO" | grep -o '"email":"[^"]*' | sed 's/"email":"//')"
    echo "Role: $(echo "$USER_INFO" | grep -o '"role":"[^"]*' | sed 's/"role":"//')"
else
    echo -e "${RED}❌ Authenticated request failed${NC}"
    echo "Response: $USER_INFO"
    exit 1
fi
echo ""

# Test 4: Test registration with invalid data (should fail)
echo "4️⃣ Testing registration validation..."
INVALID_REG=$(curl -s -X POST http://localhost:8000/api/v1/users/register \
    -H "Content-Type: application/json" \
    -d '{"username":"ab","password":"123"}')

if echo "$INVALID_REG" | grep -q "detail"; then
    echo -e "${GREEN}✅ Validation working (correctly rejected invalid data)${NC}"
else
    echo -e "${YELLOW}⚠️  Validation might not be working as expected${NC}"
fi
echo ""

# Test 5: Frontend accessibility
echo "5️⃣ Testing frontend availability..."
FRONTEND=$(curl -s http://localhost:5173)
if echo "$FRONTEND" | grep -q "html"; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 All authentication tests passed!${NC}"
echo ""
echo "📝 Next Steps:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Login with: admin / admin123"
echo "3. Test the dashboard features"
echo ""
echo "📚 Documentation: docs/AUTHENTICATION_FIXES.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
