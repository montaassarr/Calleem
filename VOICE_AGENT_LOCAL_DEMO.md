# Voice Agent Local Demo

## Overview

This is a simplified local demo version of the voice agent feature. Instead of integrating with external voice services (like Vapi), all functionality works locally within the dashboard.

## What Works

### 1. Voice Configuration (Settings Page)
- **Model Selection**: Choose from Groq AI models (llama-3.3-70b-versatile, llama-3.1-70b-versatile, etc.)
- **Voice Selection**: Select from 100+ ElevenLabs voices with preview
- **Prompt Customization**: Edit system prompt and first message with dynamic variables
- **Tool Management**: Enable/disable appointment management tools
- **Saving**: All settings saved to MongoDB database

### 2. Voice Test Page
- **Configuration Test**: Verify your voice settings are valid
- **Local Demo Mode**: Shows how the voice agent would work in production
- **Flow Visualization**: Displays the 5-step conversation flow

### 3. Voice Control Room (Index Page)
- **Call History**: View all simulated voice interactions
- **Analytics**: See call statistics and trends
- **Real-time Status**: Monitor active sessions (in demo mode)

## How It Works (Local Demo)

### Current Implementation

1. **Configuration Endpoints** (`/voice/config`)
   - GET: Fetches voice configuration from MongoDB
   - PUT: Saves voice configuration to MongoDB
   - Works: ✅ Fully functional

2. **Test Endpoint** (`/voice/test`)
   - Returns: Local demo configuration from database
   - Response: `{"status": "ok", "mode": "local_demo", "config": {...}}`
   - Works: ✅ Fully functional

3. **Start Call Endpoint** (`/voice/start-call`)
   - Logs call to `voice_calls` collection in MongoDB
   - Status: Set to "demo_mode"
   - Works: ✅ Fully functional (simulated)

4. **Call History Endpoint** (`/voice/call-history`)
   - Queries `voice_calls` collection directly
   - Returns: All logged calls
   - Works: ✅ Fully functional

### Database Schema

Voice configurations are stored in MongoDB:

```python
{
    "business_id": "default",
    "model": "groq:llama-3.3-70b-versatile",
    "voice": "elevenlabs:Rachel",
    "first_message": "Hello! Welcome to {{business_name}}...",
    "system_prompt": "You are Ava, an AI receptionist...",
    "enabled_tools": [
        "check_availability",
        "book_appointment",
        "get_services"
    ],
    "temperature": 0.7,
    "enable_recording": true
}
```

Call logs are stored in the `voice_calls` collection:

```python
{
    "business_id": "default",
    "from_number": "+1234567890",
    "status": "demo_mode",
    "created_at": "2025-01-19T12:00:00",
    "duration": 0,
    "recording_url": null
}
```

## File Changes Made

### Backend Files

1. **`backend/routers/voice.py`**
   - Removed all Vapi API dependencies
   - Changed endpoints to work with MongoDB directly
   - Added "local_demo" mode responses
   - Fixed database comparison bugs (`if db is None:`)

2. **`backend/models/business_config.py`**
   - VoiceConfiguration model (already complete)
   - All fields properly defined

3. **`backend/services/elevenlabs_service.py`**
   - ElevenLabs API integration (working)
   - Fetches available voices

### Frontend Files

1. **`frontend/src/pages/VoiceAgent/Settings.tsx`**
   - 4-tab interface (Model, Voice, Prompt, Tools)
   - Fixed useState→useEffect hook issue
   - Fully functional configuration UI

2. **`frontend/src/pages/VoiceAgent/Test.tsx`**
   - **UPDATED**: Removed Vapi WebRTC client
   - Shows "Local Demo Mode" banner
   - Displays configuration test results
   - Shows 5-step flow visualization

3. **`frontend/src/pages/VoiceAgent/Index.tsx`**
   - Control room dashboard (unchanged)
   - Works with updated endpoints

## Testing the Demo

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Navigate to Voice Agent**:
   - Go to `http://localhost:5173/voice-agent/settings`
   - Configure your voice settings
   - Click Save
   - Go to Test page
   - Click "Run Test"

### Database Verification & CRUD Demo

Need to prove the voice agent shares the exact MongoDB collections with WhatsApp? Run the helper script:

```
python backend/scripts/voice_crud_demo.py
```

It performs a full create/read/update/delete cycle on the `business_configs` collection, printing the active prompt, first message, enabled tool list, and advanced voice options. Because the same collection powers both WhatsApp and the voice agent, any changes you see in this script are the values the dashboard and conversation engine consume.

## What's Different from Production?

### Local Demo Mode
- ❌ No actual voice calls
- ❌ No WebRTC integration
- ❌ No Vapi API calls
- ✅ All settings saved to database
- ✅ Configuration UI fully functional
- ✅ Call logging works (simulated)
- ✅ Shows how it would work in production

### Production Mode (Not Implemented)
- ✅ Real voice calls via Vapi or similar
- ✅ WebRTC browser sessions
- ✅ Actual phone number integration
- ✅ Real-time transcription
- ✅ Call recording and playback

## Benefits of Local Demo

1. **Test Configuration**: Verify your settings work correctly
2. **No External Dependencies**: Works without Vapi API keys
3. **Faster Development**: Test UI changes without API calls
4. **Cost-Free**: No charges for test calls
5. **Educational**: Shows the system architecture

## Next Steps for Production

To convert this to a production voice agent:

1. **Choose Voice Provider**:
   - Vapi (recommended for ease)
   - Twilio + Groq + ElevenLabs
   - Bland AI
   - Custom WebRTC solution

2. **Update Endpoints**:
   - Implement actual call creation
   - Add WebRTC session management
   - Handle real-time events
   - Process transcripts

3. **Add Phone Integration**:
   - Configure phone numbers
   - Set up webhooks
   - Handle inbound/outbound calls

4. **Implement Recording**:
   - Store call recordings
   - Link to appointments
   - Playback in dashboard

## Troubleshooting

### Backend Not Starting
- Install missing packages: `pip install email-validator`
- Check MongoDB is running: `mongosh`
- Verify .env file has required keys

### Frontend Errors
- Install dependencies: `npm install`
- Check backend is running on port 8001
- Clear browser cache

### Configuration Not Saving
- Check MongoDB connection
- Verify business_id in requests
- Check browser console for errors

## Summary

This local demo shows how the voice agent would work without requiring external API integrations. All configuration is functional and saved to the database. The UI demonstrates the complete workflow from configuration to testing. This provides a foundation for implementing a production voice system when ready.
