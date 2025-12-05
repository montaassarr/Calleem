# Voice Agent Testing Guide

## Quick Start

### 1. Web Interface Test

1. **Start all services:**
   ```bash
   ./start.sh
   ```

2. **Ensure agent worker is running:**
   ```bash
   cd livekit-agent-worker
   python3 tenant_agent.py dev
   ```

3. **Open browser:**
   - Go to: http://localhost:3000
   - Login with: `montamsallem@gmail.com` / `Mariemmontassar03$`
   - Navigate to: **Voice AI → Test Voice Agent**

4. **Start test:**
   - Click "Start Test Call"
   - **IMPORTANT**: Click the green "🔊 Click to Enable Audio" button
   - Allow microphone access
   - Start speaking!

### 2. Terminal Voice Test

Use the Python script for terminal-based voice interaction:

```bash
# Install dependencies (if needed)
pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-silero pyaudio requests numpy

# On Linux, you may need:
sudo apt-get install portaudio19-dev python3-pyaudio

# Run the script
python3 talk_to_ai.py
```

The script will:
1. Login to backend
2. Create LiveKit session
3. Connect to room
4. Start microphone capture
5. Play AI responses through speakers

## Troubleshooting

### Frontend Error: "Failed to create test session: fetch failed"

**Possible causes:**
1. Backend not running
   - Check: `curl http://localhost:8000/health`
   - Start backend if needed

2. Backend URL incorrect
   - Check `.env.local` in `frontend_next/`
   - Should have: `NEXT_PUBLIC_API_URL=http://localhost:8000`

3. LiveKit not configured
   - Check backend `.env` for:
     - `LIVEKIT_URL`
     - `LIVEKIT_API_KEY`
     - `LIVEKIT_API_SECRET`

4. Authentication token missing
   - Make sure you're logged in
   - Check browser console for auth errors

### No Audio from AI

**Check these:**

1. **Audio button clicked?**
   - Must click green "Enable Audio" button
   - Button should disappear after enabling

2. **Browser permissions?**
   - Allow microphone access
   - Check browser settings

3. **Agent worker running?**
   ```bash
   cd livekit-agent-worker
   python3 tenant_agent.py dev
   ```
   - Should see: "registered worker"
   - Should see: "Agent session started"

4. **TTS API key configured?**
   - Go to: Settings → API Keys
   - Need at least one TTS provider:
     - Cartesia (recommended, no key needed)
     - ElevenLabs
     - OpenAI
   - Need LLM provider:
     - Groq (recommended)
     - OpenAI

5. **Check agent worker logs:**
   ```bash
   tail -f livekit-agent-worker/agent.log
   ```
   - Look for TTS initialization
   - Look for errors

### Terminal Script Issues

**If script fails to connect:**

1. **Check backend:**
   ```bash
   curl http://localhost:8000/api/v1/voice-agent/webrtc/test \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Check dependencies:**
   ```bash
   pip list | grep livekit
   pip list | grep pyaudio
   ```

3. **Check microphone:**
   ```bash
   # Test microphone
   arecord -d 3 test.wav && aplay test.wav
   ```

## Testing Appointment Booking

### Via Web Interface:

1. Start test call
2. Enable audio
3. Say: **"I'd like to book an appointment for tomorrow at 2 PM"**
4. AI will ask for:
   - Your name
   - Phone number
   - Email
   - Service (if multiple)
5. AI confirms booking
6. Check Appointments page to verify

### Via Terminal:

1. Run: `python3 talk_to_ai.py`
2. Wait for "READY TO TALK!"
3. Speak the same phrase
4. Follow conversation
5. Check appointments in web interface

## Expected Flow

```
User → Frontend/Terminal
  ↓
Backend API (/api/v1/voice-agent/webrtc/test)
  ↓ Creates LiveKit Room
  ↓
Agent Worker Joins
  ↓ Fetches tenant config
  ↓ Initializes TTS/LLM
  ↓
User speaks → STT → LLM → TTS → User hears
```

## Debug Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check LiveKit connection
curl http://localhost:8000/api/v1/voice-agent/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# View agent worker logs
tail -f livekit-agent-worker/agent.log

# View backend logs (if running in Docker)
docker compose logs -f core-service

# View frontend logs
docker compose logs -f frontend
```

## Common Issues

### Issue: "No TTS API key found"
**Solution:** Add TTS API key in Settings → API Keys

### Issue: "Agent not responding"
**Solution:** 
- Check agent worker is running
- Check agent worker logs for errors
- Verify API keys are correct

### Issue: "Room not found"
**Solution:**
- Backend may not have created room
- Check backend logs
- Try creating session again

### Issue: "Microphone not working"
**Solution:**
- Check browser/system microphone permissions
- Test microphone in another app
- Check browser console for errors

## Next Steps

After successful test:
1. ✅ Voice works
2. ✅ Appointment booking works
3. ✅ Transcript appears
4. ✅ Appointments saved to database

Then you can:
- Customize AI personality in Settings → AI
- Add more services
- Configure business hours
- Set up phone numbers

