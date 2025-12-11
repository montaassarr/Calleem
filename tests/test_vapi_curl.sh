#!/bin/bash
# Vapi E2E Test Commands
# Run these commands to test the Vapi integration

# =============================================================================
# CONFIGURATION
# =============================================================================
VAPI_API_KEY="REDACTED"
VAPI_PUBLIC_KEY="REDACTED"
VAPI_ORG_ID="255c8f85-eb22-47f0-b3ea-9537340f79fb"

# Created assistants from E2E test
BELLA_ASSISTANT_ID="8c250351-532d-4399-9b0c-85ec8bde4f1e"
DENTAL_ASSISTANT_ID="c44cbbdb-4fc4-4774-8b1d-92342da80bc8"

echo "==================================================================="
echo "🧪 VAPI E2E TEST COMMANDS"
echo "==================================================================="

# =============================================================================
# TEST 1: List all assistants
# =============================================================================
echo ""
echo "📋 TEST 1: List all assistants in your Vapi account"
echo "-------------------------------------------------------------------"
curl -s -X GET "https://api.vapi.ai/assistant" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Found {len(data)} assistants:')
for a in data:
    print(f\"  - {a.get('name', 'Unnamed')}: {a.get('id')}\")"

# =============================================================================
# TEST 2: Get specific assistant details
# =============================================================================
echo ""
echo "📖 TEST 2: Get Bella's Hair Salon assistant details"
echo "-------------------------------------------------------------------"
curl -s -X GET "https://api.vapi.ai/assistant/$BELLA_ASSISTANT_ID" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Name: {data.get('name')}\")"

# =============================================================================
# TEST 3: Simulate function call (checkAvailability)
# This is what Vapi would send to your webhook
# =============================================================================
echo ""
echo "🔧 TEST 3: Simulate checkAvailability function call to backend webhook"
echo "-------------------------------------------------------------------"
curl -s -X POST "http://localhost:8000/api/v1/vapi/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "call": {
        "id": "test-call-001",
        "metadata": {
          "tenant_id": "test-tenant-001"
        }
      },
      "functionCall": {
        "name": "checkAvailability",
        "parameters": {
          "date": "2025-12-15"
        }
      }
    }
  }' | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"Response: {json.dumps(data, indent=2)}\")
except:
    print('Response received')"

# =============================================================================
# TEST 4: Simulate bookAppointment function call
# =============================================================================
echo ""
echo "📅 TEST 4: Simulate bookAppointment function call to backend webhook"
echo "-------------------------------------------------------------------"
curl -s -X POST "http://localhost:8000/api/v1/vapi/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "call": {
        "id": "test-call-002",
        "metadata": {
          "tenant_id": "test-tenant-001"
        }
      },
      "functionCall": {
        "name": "bookAppointment",
        "parameters": {
          "date": "2025-12-15",
          "time": "14:00",
          "name": "John Doe",
          "phone": "+1234567890",
          "service": "Haircut"
        }
      }
    }
  }' | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"Response: {json.dumps(data, indent=2)}\")
except:
    print('Response received')"

# =============================================================================
# TEST 5: Start a web call (for testing in browser)
# =============================================================================
echo ""
echo "🌐 TEST 5: Web call configuration for browser testing"
echo "-------------------------------------------------------------------"
echo "To test in browser, use this configuration in your frontend:"
echo ""
echo "const vapi = new Vapi('$VAPI_PUBLIC_KEY');"
echo "vapi.start({assistantId: '$BELLA_ASSISTANT_ID'});"
echo ""
echo "Or open: https://dashboard.vapi.ai/assistants/$BELLA_ASSISTANT_ID"

echo ""
echo "==================================================================="
echo "✅ TEST COMMANDS COMPLETE"
echo "==================================================================="
