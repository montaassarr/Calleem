#!/bin/bash

# Get ngrok URL and display webhook configuration

echo "========================================"
echo "🌐 AI Receptionist - ngrok URL"
echo "========================================"
echo ""

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ ngrok is not running!"
    echo ""
    echo "Start ngrok with: ngrok http 8000"
    exit 1
fi

echo "✅ ngrok is running"
echo ""
echo "📍 Public URL:"
echo "   $NGROK_URL"
echo ""
echo "📍 Webhook URL for Twilio:"
echo "   $NGROK_URL/api/v1/webhook/sms"
echo ""
echo "========================================"
echo "📋 Twilio Configuration Steps:"
echo "========================================"
echo ""
echo "1. Go to: https://console.twilio.com/"
echo "2. Navigate to: Messaging → WhatsApp Sandbox Settings"
echo "3. Set 'When a message comes in' to:"
echo "   $NGROK_URL/api/v1/webhook/sms"
echo "4. Method: POST"
echo "5. Click Save"
echo ""
echo "========================================"
echo "🧪 Test the webhook:"
echo "========================================"
echo ""
echo "curl -X POST $NGROK_URL/api/v1/webhook/sms \\"
echo "  -d 'From=whatsapp:+1234567890&Body=Hello&MessageSid=TEST'"
echo ""
