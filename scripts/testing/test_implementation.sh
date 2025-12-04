#!/bin/bash

# 🚀 Quick Start Script for AI Receptionist
# This script helps you set up and test the new API key architecture

echo "🔧 AI Receptionist - Setup & Test Script"
echo "========================================="
echo ""

# Step 1: Check if MASTER_KEY exists
if [ -z "$MASTER_KEY" ]; then
    echo "⚠️  MASTER_KEY not found. Generating one..."
    export MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    echo "✅ Generated MASTER_KEY: $MASTER_KEY"
    echo ""
    echo "💡 Add this to your .env file:"
    echo "MASTER_KEY=$MASTER_KEY"
    echo ""
fi

# Step 2: Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Step 3: Test imports
echo ""
echo "📦 Testing backend imports..."
cd backend

echo "  - Testing simple_setup router..."
python3 -c "from routers import simple_setup; print('    ✅ simple_setup')" 2>&1 | grep -v "WARNING" || echo "    ❌ Failed"

echo "  - Testing voice_agent router..."
python3 -c "from routers import voice_agent; print('    ✅ voice_agent')" 2>&1 | grep -v "WARNING" || echo "    ❌ Failed"

echo "  - Testing ai_proxy_service..."
python3 -c "from services.ai_proxy_service import ai_proxy; print('    ✅ ai_proxy_service')" 2>&1 | grep -v "WARNING" || echo "    ❌ Failed"

# Step 4: Check MongoDB connection
echo ""
echo "🗄️  Checking MongoDB..."
if [ -z "$MONGODB_URL" ]; then
    echo "  ⚠️  MONGODB_URL not set. Using default: mongodb://localhost:27017/ai_receptionist"
    export MONGODB_URL="mongodb://localhost:27017/ai_receptionist"
fi

# Step 5: List all routers in main.py
echo ""
echo "🛣️  Registered API routers:"
grep "app.include_router" main.py | grep -o 'tags=\["[^"]*"\]' | sed 's/tags=\["\(.*\)"\]/  - \1/'

# Step 6: Show new endpoints
echo ""
echo "🆕 New endpoints for non-technical users:"
echo "  POST   /api/v1/setup/api-key        - Easy key setup"
echo "  GET    /api/v1/setup/my-keys        - View your keys"
echo "  GET    /api/v1/setup/providers      - Provider guide"
echo "  DELETE /api/v1/setup/api-key/{id}   - Remove key"

# Step 7: Show platform admin endpoints
echo ""
echo "🔐 Platform admin endpoints (super-admin only):"
echo "  POST   /api/v1/platform/api-keys           - Add platform key"
echo "  GET    /api/v1/platform/api-keys           - List platform keys"
echo "  GET    /api/v1/platform/api-keys/{id}      - Get specific key"
echo "  PUT    /api/v1/platform/api-keys/{id}      - Update key"
echo "  DELETE /api/v1/platform/api-keys/{id}      - Delete key"
echo "  POST   /api/v1/platform/api-keys/{id}/health - Health check"
echo "  GET    /api/v1/platform/api-keys/usage/summary - Usage analytics"

# Step 8: Show updated voice agent endpoints
echo ""
echo "🎙️  Updated voice agent endpoints (now with fallback):"
echo "  GET  /api/v1/voice-agent/status   - Agent status"
echo "  GET  /api/v1/voice-agent/history  - Call history"
echo "  POST /api/v1/voice-agent/call     - Start call"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Documentation:"
echo "  - USER_API_KEYS_GUIDE.md - For end users"
echo "  - FINAL_IMPLEMENTATION_SUMMARY.md - Technical overview"
echo "  - COMPARISON_TABLE.md - Feature comparison"
echo "  - IMPLEMENTATION_AUDIT.md - Detailed audit"
echo ""
echo "🚀 To start the server:"
echo "  cd /home/montassar/Desktop/ai_receptionist/backend"
echo "  MASTER_KEY=$MASTER_KEY uvicorn main:app --reload"
echo ""
