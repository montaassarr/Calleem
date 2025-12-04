#!/bin/bash

echo "=========================================="
echo "🚀 AI Receptionist - System Status Check"
echo "=========================================="
echo ""

# Check Backend
echo "📡 Backend API:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:8000"
else
    echo "   ❌ Not running"
fi
echo ""

# Check Frontend
echo "🌐 Frontend:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:3000"
else
    echo "   ❌ Not running"
fi
echo ""

# Check LiveKit Agent
echo "🤖 LiveKit Agent Worker:"
if ps aux | grep -q "[l]ivekit-agent-worker"; then
    echo "   ✅ Running"
    AGENT_PROCESS=$(ps aux | grep "[l]ivekit-agent-worker.*spawn_main" | head -1)
    if [ -n "$AGENT_PROCESS" ]; then
        echo "   📊 Worker processes active"
    fi
else
    echo "   ❌ Not running"
fi
echo ""

# Check MongoDB
echo "💾 MongoDB:"
if pgrep -x mongod > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi
echo ""

# Check n8n
echo "🔄 n8n Automation:"
if docker ps | grep -q "n8n"; then
    echo "   ✅ Running on http://localhost:5678"
else
    echo "   ⚠️  Not running (optional)"
fi
echo ""

# Check API Keys
echo "🔑 API Keys Configuration:"
python3 << 'PYEOF'
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["callflow_ai_saas"]
config = db.business_config.find_one({"tenant_id": "692f43697c982c08898e127b"})
if config and config.get("api_keys"):
    api_keys = config.get("api_keys", [])
    providers = [key.get("provider") for key in api_keys if key.get("provider")]
    print(f"   ✅ Configured: {', '.join(providers)}")
else:
    print("   ❌ No API keys found")
PYEOF
echo ""

echo "=========================================="
echo "📝 Quick Links:"
echo "=========================================="
echo ""
echo "🔐 Login: http://localhost:3000/login"
echo "🎙️  Voice Chat (NEW): http://localhost:3000/dashboard/voice-agent/chat-new"
echo "📊 Dashboard: http://localhost:3000/dashboard"
echo "🔄 n8n: http://localhost:5678"
echo ""

echo "=========================================="
echo "🧪 Test Voice Agent:"
echo "=========================================="
echo ""
echo "1. Open: http://localhost:3000/login"
echo "2. Login with: montamsallem@gmail.com"
echo "3. Go to: Dashboard → Voice Agent → Chat"
echo "4. Click 'Start Chat'"
echo "5. Allow microphone permission"
echo "6. Say: 'Hello, I'd like to book an appointment for tomorrow at 2 PM'"
echo ""
echo "You should hear the AI respond with voice! 🎉"
echo ""
