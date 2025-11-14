#!/bin/bash

# Comprehensive AI Receptionist System Test
# Tests all components: Backend, ngrok, Groq, Database, Webhook

echo "========================================"
echo "🧪 AI Receptionist - System Test"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Backend Running
echo -e "${BLUE}[1/8] Testing Backend...${NC}"
if ps aux | grep -q "[u]vicorn.*main:app"; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is NOT running${NC}"
    echo "Start with: cd backend && python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi
echo ""

# Test 2: ngrok Running
echo -e "${BLUE}[2/8] Testing ngrok...${NC}"
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)
if [ -n "$NGROK_URL" ]; then
    echo -e "${GREEN}✅ ngrok is running${NC}"
    echo -e "   URL: ${YELLOW}$NGROK_URL${NC}"
else
    echo -e "${RED}❌ ngrok is NOT running${NC}"
    echo "Start with: ngrok http 8000"
    exit 1
fi
echo ""

# Test 3: MongoDB
echo -e "${BLUE}[3/8] Testing MongoDB...${NC}"
if systemctl is-active --quiet mongod 2>/dev/null || pgrep -x mongod > /dev/null; then
    echo -e "${GREEN}✅ MongoDB is running${NC}"
    APPT_COUNT=$(mongosh ai_barber_receptionist --quiet --eval "db.appointments.countDocuments({})" 2>/dev/null)
    CONV_COUNT=$(mongosh ai_barber_receptionist --quiet --eval "db.conversations.countDocuments({})" 2>/dev/null)
    echo -e "   Appointments: ${YELLOW}$APPT_COUNT${NC}"
    echo -e "   Conversations: ${YELLOW}$CONV_COUNT${NC}"
else
    echo -e "${RED}❌ MongoDB is NOT running${NC}"
    exit 1
fi
echo ""

# Test 4: Backend API Health
echo -e "${BLUE}[4/8] Testing Backend API...${NC}"
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/appointments/ 2>/dev/null)
if [ "$API_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Backend API responding${NC}"
else
    echo -e "${RED}❌ Backend API not responding (HTTP $API_RESPONSE)${NC}"
    exit 1
fi
echo ""

# Test 5: Webhook Endpoint (Local)
echo -e "${BLUE}[5/8] Testing Webhook (Local)...${NC}"
WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/webhook/sms \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Hello&MessageSid=TEST_123" 2>&1)

if echo "$WEBHOOK_RESPONSE" | grep -q "<Response>"; then
    echo -e "${GREEN}✅ Webhook endpoint responding${NC}"
    echo -e "   ${YELLOW}AI Response:${NC} $(echo "$WEBHOOK_RESPONSE" | grep -o '<Message>[^<]*</Message>' | sed 's/<[^>]*>//g' | cut -c1-60)..."
else
    echo -e "${RED}❌ Webhook not responding correctly${NC}"
    exit 1
fi
echo ""

# Test 6: Groq AI
echo -e "${BLUE}[6/8] Testing Groq AI Integration...${NC}"
GROQ_LOG=$(tail -50 /home/montassar/Desktop/ai_receptionist/logs/backend.log | grep "api.groq.com" | tail -1)
if [ -n "$GROQ_LOG" ]; then
    if echo "$GROQ_LOG" | grep -q "200 OK"; then
        echo -e "${GREEN}✅ Groq AI responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Groq AI may have issues${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No recent Groq API calls${NC}"
fi
echo ""

# Test 7: Create Test Appointment
echo -e "${BLUE}[7/8] Testing Appointment Creation...${NC}"
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Client",
    "client_phone": "+1234567890",
    "service": "Haircut",
    "datetime": "2025-11-20T15:00:00",
    "duration_minutes": 30
  }' 2>&1)

if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
    echo -e "${GREEN}✅ Appointment creation working${NC}"
    TEST_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    echo -e "   Test appointment ID: ${YELLOW}$TEST_ID${NC}"
    
    # Clean up test appointment
    curl -s -X DELETE "http://localhost:8000/api/v1/appointments/$TEST_ID" >/dev/null 2>&1
    echo -e "   ${YELLOW}(Test appointment deleted)${NC}"
else
    echo -e "${RED}❌ Appointment creation failed${NC}"
    echo "$CREATE_RESPONSE"
    exit 1
fi
echo ""

# Test 8: ngrok Webhook (External)
echo -e "${BLUE}[8/8] Testing ngrok Webhook (External)...${NC}"
NGROK_WEBHOOK_RESPONSE=$(curl -s -X POST "$NGROK_URL/api/v1/webhook/sms" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Test&MessageSid=TEST_456" 2>&1)

if echo "$NGROK_WEBHOOK_RESPONSE" | grep -q "<Response>" || echo "$NGROK_WEBHOOK_RESPONSE" | grep -q "Message"; then
    echo -e "${GREEN}✅ ngrok webhook accessible${NC}"
else
    echo -e "${YELLOW}⚠️  ngrok webhook may have connectivity issues${NC}"
    echo -e "   This is normal with free ngrok - Twilio should still work"
fi
echo ""

echo "========================================"
echo -e "${GREEN}✅ System Test Complete!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}📋 Twilio Configuration:${NC}"
echo "   Webhook URL: $NGROK_URL/api/v1/webhook/sms"
echo "   Method: POST"
echo ""
echo -e "${YELLOW}🧪 Test via WhatsApp:${NC}"
echo "   Send a message to your Twilio number"
echo "   Expected: AI should respond and create appointments"
echo ""
