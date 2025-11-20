# Vapi Integration Guide

## ✅ Integration Complete

Your AI Receptionist now uses the official Vapi SDK for professional voice calls with real-time transcription and natural conversations.

## What Was Integrated

### Frontend (`@vapi-ai/web` v2.5.1)
- **Component**: `frontend/src/pages/VoiceAgent/VoiceChatVapi.tsx`
- **Features**:
  - Real-time voice calls with WebRTC
  - Live conversation transcription
  - Volume indicators and speaking status
  - Mute/unmute controls
  - Professional call UI with status badges
  
### Backend (`vapi-server-sdk` v1.9.0)
- **Service**: `backend/services/vapi_service.py`
- **Endpoint**: `GET /api/v1/voice/vapi-config`
- **Features**:
  - Automatic assistant creation from voice configuration
  - Model support: Groq, OpenAI, Anthropic
  - Voice providers: ElevenLabs, PlayHT, etc.
  - Deepgram transcription
  - Tool/function calling support (when webhook configured)

## Setup Instructions

### 1. Get Your Vapi Public Key

1. Go to https://dashboard.vapi.ai
2. Navigate to **Settings → API Keys**
3. Copy your **Public Key**

### 2. Update Environment Variables

Edit `backend/.env`:

```env
# Your API key is already configured
VAPI_API_KEY=REDACTED

# Add your public key here
VAPI_PUBLIC_KEY=REDACTED

# Optional: For function calling (appointment booking via voice)
VAPI_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/api/v1/voice/webhook
```

### 3. Restart Backend

```bash
cd backend
python main.py
```

### 4. Test the Integration

1. Open http://localhost:5173
2. Login to the dashboard
3. Navigate to **Voice Agent → Chat**
4. Click **Start Call**
5. Speak: "I'd like to book an appointment"
6. The AI will respond with voice and you'll see live transcription

## How It Works

### Call Flow
```
1. User clicks "Start Call"
2. Frontend fetches config from /voice/vapi-config
3. Backend creates/retrieves Vapi assistant
4. Returns publicKey + assistantId
5. Frontend initializes Vapi client
6. Vapi establishes WebRTC connection
7. Real-time voice conversation begins
```

### Voice Configuration
The assistant uses your voice settings from the Voice Agent dashboard:
- **Model**: `groq:llama-3.3-70b-versatile`
- **Voice**: `elevenlabs:Rachel`
- **System Prompt**: Your custom instructions
- **First Message**: Greeting when call starts
- **Temperature**: Controls response randomness

### Function Calling (Optional)
When `VAPI_WEBHOOK_URL` is configured:
1. AI detects user intent (e.g., "book appointment")
2. Calls your webhook with function request
3. Backend executes the function (creates appointment)
4. Returns result to Vapi
5. AI speaks the confirmation

## Testing Without Public Key

If you don't have the public key yet, the frontend will show:
```
⚠️ Configuration Required
Vapi is not configured. Please set VAPI_PUBLIC_KEY in .env
```

## Repository Structure

```
ai-_receptionist/
├── vapi-client-sdk/          # Reference: Vapi web SDK source
├── vapi-server-sdk/          # Reference: Vapi Python SDK source
├── backend/
│   ├── services/
│   │   └── vapi_service.py   # Vapi integration service
│   ├── routers/
│   │   └── voice.py          # /vapi-config endpoint
│   └── .env                  # Add VAPI_PUBLIC_KEY here
└── frontend/
    └── src/
        └── pages/VoiceAgent/
            └── VoiceChatVapi.tsx  # Voice chat interface
```

## Troubleshooting

### "Configuration Required" Error
- Check `VAPI_PUBLIC_KEY` is set in `backend/.env`
- Restart backend after updating `.env`

### No Audio
- Check browser microphone permissions
- Ensure speakers/headphones are connected
- Check browser console for WebRTC errors

### Assistant Not Created
- Check `VAPI_API_KEY` is valid
- View backend logs: `backend/logs/app.log`
- Verify MongoDB is running

### WebRTC Connection Failed
- Check firewall settings
- Try different browser (Chrome recommended)
- Check network allows WebRTC/UDP traffic

## Next Steps

1. **Configure Webhook** for appointment booking via voice
2. **Customize Voice** in Voice Agent → Settings
3. **Test Different Models** (Groq, OpenAI, Anthropic)
4. **Add Custom Tools** for specific business functions
5. **Monitor Calls** in Vapi dashboard

## Resources

- [Vapi Documentation](https://docs.vapi.ai)
- [Vapi Dashboard](https://dashboard.vapi.ai)
- [Vapi Client SDK](https://github.com/VapiAI/client-sdk-web)
- [Vapi Server SDK](https://github.com/VapiAI/server-sdk-python)

---

**Status**: ✅ Integration complete, waiting for `VAPI_PUBLIC_KEY` configuration
