# Voice Agent Architecture Consolidation

## Summary
Consolidated duplicate voice agent pages into a single unified test page with improved audio handling and better user experience.

## Changes Made

### 1. Removed Duplicate Pages
- ❌ **Deleted**: `/dashboard/ai-receptionist/page.tsx` (duplicate of voice agent test)
- ❌ **Deleted**: `/dashboard/voice-agent/chat/page.tsx` (merged into test page)

### 2. Unified Test Page
- ✅ **Updated**: `/dashboard/voice-agent/test/page.tsx`
  - Now includes voice + chat transcript in one interface
  - Better error handling and connection status
  - Clear instructions for users
  - Uses `VoiceAppWithChat` component for full functionality

### 3. Updated Navigation
- ✅ **Updated**: Sidebar now shows:
  - Voice AI → Control Center
  - Voice AI → Test Voice Agent (single option)
- ✅ **Updated**: All internal links now point to `/dashboard/voice-agent/test`

### 4. Audio Improvements
- ✅ **Enhanced**: `VoiceAppWithChat` component
  - Added proper audio configuration options
  - Improved RoomAudioRenderer setup
  - Better debugging for audio track availability
  - Clear instructions for enabling audio

### 5. Updated References
- ✅ Fixed links in:
  - `/dashboard/settings/ai/page.tsx` (2 links)
  - `/dashboard/page.tsx` (1 link)
  - `/components/dashboard/ProOnboardingChecklist.tsx` (1 link)

## How to Use

### Testing Voice Agent

1. **Navigate to Test Page**
   - Go to: Dashboard → Voice AI → Test Voice Agent
   - Or directly: `/dashboard/voice-agent/test`

2. **Start Test Call**
   - Click "Start Test Call" button
   - Wait for connection (green status indicator)

3. **Enable Audio**
   - Click the green "🔊 Click to Enable Audio" button at the top
   - This is **critical** - you won't hear AI without this!

4. **Speak to AI**
   - Allow microphone access when prompted
   - Try: "I'd like to book an appointment for tomorrow at 2 PM"
   - Or: "What services do you offer?"

5. **View Transcript**
   - Right panel shows live conversation transcript
   - Both voice and text messages appear in real-time

### Troubleshooting Audio Issues

**If you can't hear the AI:**

1. **Check Audio Button**
   - Look for green "Enable Audio" button at top of screen
   - Click it if you haven't already
   - Button should disappear after enabling

2. **Check Browser Permissions**
   - Ensure microphone is allowed
   - Check browser console for errors

3. **Check Agent Worker**
   - Verify agent worker is running: `cd livekit-agent-worker && ./start.sh`
   - Check logs: `tail -f agent.log`
   - Look for TTS initialization messages

4. **Check API Keys**
   - Go to Settings → API Keys
   - Ensure you have at least one TTS provider configured:
     - Cartesia (recommended, no key needed)
     - ElevenLabs
     - OpenAI
   - Ensure you have an LLM provider:
     - Groq (recommended)
     - OpenAI

5. **Check Backend Connection**
   - Verify backend is running: `http://localhost:8000/health`
   - Check tenant config endpoint: `http://localhost:8000/api/v1/voice-agent/tenant-config/{tenant_id}`

## Architecture Flow

```
User → Frontend Test Page
  ↓
Next.js API Route (/api/connection-details)
  ↓
Backend API (/api/v1/voice-agent/webrtc/test)
  ↓ Creates LiveKit Room with tenant_id metadata
  ↓
LiveKit Room Created
  ↓
Agent Worker Joins Room
  ↓ Extracts tenant_id from room metadata
  ↓
Backend API (/api/v1/voice-agent/tenant-config/{tenant_id})
  ↓ Returns API keys and agent config
  ↓
Agent Worker Initializes:
  - STT (Deepgram)
  - LLM (Groq/OpenAI)
  - TTS (Cartesia/ElevenLabs/OpenAI)
  - VAD (Silero)
  ↓
Agent Session Started
  ↓
User can now speak and hear AI responses
```

## Key Files

### Frontend
- `/frontend_next/app/dashboard/voice-agent/test/page.tsx` - Main test page
- `/frontend_next/components/voice-agent/voice-app-with-chat.tsx` - Voice + chat component
- `/frontend_next/app/api/connection-details/route.ts` - API route for LiveKit tokens

### Backend
- `/backend/routers/voice_agent.py` - Voice agent API endpoints
  - `POST /api/v1/voice-agent/webrtc/test` - Create test session
  - `GET /api/v1/voice-agent/tenant-config/{tenant_id}` - Get tenant config

### Agent Worker
- `/livekit-agent-worker/tenant_agent.py` - Multi-tenant agent implementation
  - Fetches config per tenant
  - Initializes TTS/LLM based on available API keys
  - Handles appointment booking and other tools

## Next Steps

1. **Test the flow:**
   - Login with: montamsallem@gmail.com
   - Navigate to Voice AI → Test Voice Agent
   - Start a call and test appointment booking

2. **Verify audio:**
   - Ensure you can hear AI responses
   - Check that transcript appears in real-time

3. **Test appointment booking:**
   - Say: "I'd like to book an appointment for tomorrow at 2 PM"
   - Provide details when asked
   - Verify appointment appears in Appointments page

## Notes

- The agent worker must be running for voice to work
- TTS API key is required (Cartesia recommended, no key needed)
- LLM API key is required (Groq or OpenAI)
- Audio must be explicitly enabled via the green button
- RoomAudioRenderer handles audio output from agent

