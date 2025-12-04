#!/bin/bash

# Quick diagnostic script for CallFlow AI agent issues

echo "🔍 CallFlow AI - Agent Diagnostics"
echo "=================================="
echo ""

TENANT_ID="692f43697c982c08898e127b"
BACKEND_URL="http://localhost:8000"

echo "📋 Your Configuration:"
echo "  Tenant ID: $TENANT_ID"
echo "  Backend: $BACKEND_URL"
echo ""

# 1. Check Backend
echo "1️⃣ Checking Backend..."
if curl -s -f "$BACKEND_URL/docs" > /dev/null 2>&1; then
    echo "  ✅ Backend is running"
else
    echo "  ❌ Backend not accessible"
    exit 1
fi
echo ""

# 2. Check Tenant Config
echo "2️⃣ Checking Tenant Config..."
TENANT_CONFIG=$(curl -s "$BACKEND_URL/voice-agent/tenant-config/$TENANT_ID")
if echo "$TENANT_CONFIG" | grep -q "detail"; then
    echo "  ❌ Tenant config not found"
    echo "  Response: $TENANT_CONFIG"
    echo ""
    echo "  🔧 FIX NEEDED: You need to:"
    echo "     1. Go to: http://localhost:3000/dashboard/voice-agent/control-center"
    echo "     2. Create or edit your agent"
    echo "     3. Add a system prompt like: 'You are a helpful AI receptionist'"
    echo "     4. Save the agent"
else
    echo "  ✅ Tenant config found"
    echo "$TENANT_CONFIG" | python3 -m json.tool 2>/dev/null || echo "$TENANT_CONFIG"
fi
echo ""

# 3. Check API Keys
echo "3️⃣ Checking API Keys..."
API_KEYS=$(curl -s -H "Authorization: Bearer YOUR_TOKEN" "$BACKEND_URL/keys" 2>/dev/null)
echo "  Note: Cannot check without auth token"
echo "  Please verify at: http://localhost:3000/dashboard/settings/api-keys"
echo ""

# 4. Check Agent Worker
echo "4️⃣ Checking Agent Worker..."
if ps aux | grep -q "python main.py dev" | grep -v grep; then
    echo "  ✅ Agent worker is running"
    echo "  PID: $(ps aux | grep 'python main.py dev' | grep -v grep | awk '{print $2}' | head -1)"
else
    echo "  ❌ Agent worker not running"
    echo ""
    echo "  🔧 FIX: Start the agent worker:"
    echo "     cd livekit-agent-worker"
    echo "     ./start.sh"
fi
echo ""

# 5. Check LiveKit Connectivity
echo "5️⃣ Checking LiveKit..."
if curl -s -X POST "https://aireceptionist-iqt10ym2.livekit.cloud" > /dev/null 2>&1; then
    echo "  ✅ LiveKit server reachable"
else
    echo "  ⚠️  LiveKit server check inconclusive"
fi
echo ""

echo "=================================="
echo "📝 NEXT STEPS:"
echo ""
echo "If tenant config is missing:"
echo "  1. Open: http://localhost:3000/dashboard/voice-agent/control-center"
echo "  2. Click 'Create Agent' or edit existing agent"
echo "  3. Fill in:"
echo "     - Name: My AI Receptionist"
echo "     - System Prompt: You are a helpful receptionist at my business"
echo "     - LLM Model: llama-3.3-70b-versatile"
echo "     - Voice: Select any voice"
echo "  4. Click 'Save'"
echo ""
echo "Then test again at:"
echo "  http://localhost:3000/dashboard/voice-agent/test"
echo ""
