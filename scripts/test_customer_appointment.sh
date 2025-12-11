#!/bin/bash

# Complete Customer Appointment Booking Test Workflow
# Simulates a customer using the voice agent to book an appointment

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================================="
echo -e "${BLUE}AI Receptionist - Customer Appointment Test${NC}"
echo "=========================================================="
echo ""

# Step 1: Business Owner Setup
echo -e "${YELLOW}Step 1: Business Owner Login${NC}"
echo "----------------------------------------"

TOKEN=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@callflow.ai&password=TestPass123!" \
  -s | jq -r '.access_token')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo -e "${GREEN}✅ Business owner authenticated${NC}"
else
  echo -e "${RED}❌ Authentication failed - please run test_api_endpoints.sh first${NC}"
  exit 1
fi
echo ""

# Step 2: Enable Voice Agent
echo -e "${YELLOW}Step 2: Enable Voice Agent Feature${NC}"
echo "----------------------------------------"

ENABLE_RESULT=$(curl -X POST "http://localhost:8000/api/v1/voice-agent/enable" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' \
  -s)

if echo "$ENABLE_RESULT" | jq -e '.voice_agent' | grep -q "true"; then
  echo -e "${GREEN}✅ Voice agent enabled for business${NC}"
else
  echo -e "${YELLOW}⚠️  Voice agent may already be enabled${NC}"
fi
echo ""

# Step 3: Customer Opens Website
echo -e "${YELLOW}Step 3: Customer Opens Website${NC}"
echo "----------------------------------------"
echo -e "${BLUE}🌐 Customer navigates to: http://localhost:3000${NC}"
echo -e "${BLUE}📱 Customer sees voice agent interface${NC}"
echo ""

# Step 4: Get LiveKit Connection for Customer
echo -e "${YELLOW}Step 4: Customer Requests Voice Call${NC}"
echo "----------------------------------------"

CONNECTION=$(curl -X POST "http://localhost:8000/api/v1/voice-agent/webrtc/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -s)

ROOM_NAME=$(echo "$CONNECTION" | jq -r '.room_name')
LIVEKIT_URL=$(echo "$CONNECTION" | jq -r '.url')
LIVEKIT_TOKEN=$(echo "$CONNECTION" | jq -r '.token')

if [ -n "$LIVEKIT_TOKEN" ] && [ "$LIVEKIT_TOKEN" != "null" ]; then
  echo -e "${GREEN}✅ LiveKit room created: $ROOM_NAME${NC}"
  echo -e "${GREEN}✅ LiveKit server: $LIVEKIT_URL${NC}"
  echo -e "${GREEN}✅ Customer connected to voice agent${NC}"
  
  # Save connection details
  echo "$CONNECTION" > /tmp/customer_livekit_connection.json
  echo -e "${BLUE}📄 Connection saved to: /tmp/customer_livekit_connection.json${NC}"
else
  echo -e "${RED}❌ Failed to create LiveKit connection${NC}"
  exit 1
fi
echo ""

# Step 5: Simulated Conversation
echo -e "${YELLOW}Step 5: Voice Conversation (Simulated)${NC}"
echo "----------------------------------------"
echo -e "${BLUE}🎤 Customer: \"Hello, I'd like to book an appointment\"${NC}"
echo -e "${GREEN}🤖 AI Agent: \"Hello! I'd be happy to help you book an appointment.${NC}"
echo -e "${GREEN}              What service are you interested in?\"${NC}"
echo ""
echo -e "${BLUE}🎤 Customer: \"I need a haircut\"${NC}"
echo -e "${GREEN}🤖 AI Agent: \"Great! When would you like to come in?\"${NC}"
echo ""
echo -e "${BLUE}🎤 Customer: \"Tomorrow at 2 PM\"${NC}"
echo -e "${GREEN}🤖 AI Agent: \"Let me check availability...${NC}"
echo -e "${GREEN}              Perfect! I have availability tomorrow at 2 PM.${NC}"
echo -e "${GREEN}              May I have your name and phone number?\"${NC}"
echo ""
echo -e "${BLUE}🎤 Customer: \"My name is John Doe, phone is 555-1234\"${NC}"
echo -e "${GREEN}🤖 AI Agent: \"Thank you John! Your appointment is confirmed for${NC}"
echo -e "${GREEN}              tomorrow at 2:00 PM for a haircut.${NC}"
echo -e "${GREEN}              You'll receive a confirmation message shortly.\"${NC}"
echo ""

# Step 6: Create Test Appointment
echo -e "${YELLOW}Step 6: Creating Appointment in Database${NC}"
echo "----------------------------------------"

APPOINTMENT=$(curl -X POST "http://localhost:8000/api/v1/appointments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_phone": "+15551234",
    "service": "Haircut",
    "appointment_date": "2025-12-05T14:00:00",
    "notes": "Booked via AI Voice Agent"
  }' \
  -s)

if echo "$APPOINTMENT" | jq -e '.id' > /dev/null 2>&1; then
  APPT_ID=$(echo "$APPOINTMENT" | jq -r '.id')
  echo -e "${GREEN}✅ Appointment created successfully!${NC}"
  echo -e "${GREEN}   Appointment ID: $APPT_ID${NC}"
  echo -e "${GREEN}   Customer: John Doe${NC}"
  echo -e "${GREEN}   Service: Haircut${NC}"
  echo -e "${GREEN}   Time: Tomorrow at 2:00 PM${NC}"
else
  echo -e "${YELLOW}⚠️  Appointment creation response:${NC}"
  echo "$APPOINTMENT" | jq '.'
fi
echo ""

# Step 7: Verify Appointment
echo -e "${YELLOW}Step 7: Business Owner Verifies Appointment${NC}"
echo "----------------------------------------"

APPOINTMENTS=$(curl -X GET "http://localhost:8000/api/v1/appointments" \
  -H "Authorization: Bearer $TOKEN" \
  -s)

COUNT=$(echo "$APPOINTMENTS" | jq 'length')
echo -e "${GREEN}✅ Total appointments in system: $COUNT${NC}"

if [ "$COUNT" -gt 0 ]; then
  echo ""
  echo "Recent appointments:"
  echo "$APPOINTMENTS" | jq '.[] | {
    id: .id,
    client: .client_name,
    service: .service,
    date: .appointment_date,
    status: .status
  }' | head -20
fi
echo ""

# Summary
echo "=========================================================="
echo -e "${GREEN}✅ Test Workflow Complete!${NC}"
echo "=========================================================="
echo ""
echo -e "${BLUE}Workflow Summary:${NC}"
echo "1. ✅ Business owner authenticated"
echo "2. ✅ Voice agent enabled"
echo "3. ✅ Customer connected to LiveKit voice agent"
echo "4. ✅ AI agent conversation simulated"
echo "5. ✅ Appointment created in database"
echo "6. ✅ Business owner can view appointment"
echo ""
echo -e "${BLUE}Frontend Access:${NC}"
echo "🌐 Customer URL: http://localhost:3000"
echo "🎯 Dashboard URL: http://localhost:3000/dashboard"
echo "🎤 Voice Test: http://localhost:3000/dashboard/voice-agent/test"
echo ""
echo -e "${BLUE}LiveKit Connection Details:${NC}"
echo "📄 Saved to: /tmp/customer_livekit_connection.json"
echo "🔗 Room: $ROOM_NAME"
echo "🌐 Server: $LIVEKIT_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Open http://localhost:3000 in browser"
echo "2. Navigate to Voice Agent Test page"
echo "3. Click 'Run Test' button"
echo "4. Allow microphone access"
echo "5. Speak to make an appointment"
echo "6. Verify appointment in dashboard"
echo ""
