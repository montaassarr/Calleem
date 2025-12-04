# CallFlow AI - Multi-Tenant Voice Agent Worker

Production-grade LiveKit agent worker that provides isolated voice AI agents for each tenant in the CallFlow AI platform.

## Features

- 🎯 **Multi-tenant isolation** - Each tenant gets their own agent instance
- 🔑 **BYOK support** - Uses tenant-specific API keys (Groq, OpenAI, ElevenLabs)
- 🎨 **Full customization** - Custom system prompts, voices, and LLM models per tenant
- 📞 **Function calling** - Built-in appointment booking, availability checking, and service listing
- 🔄 **Real-time sync** - Fetches latest tenant config on each call

## Quick Start

### 1. Install Dependencies

```bash
cd livekit-agent-worker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` file and update if needed:

```bash
cp .env .env.local
# Edit .env.local with your LiveKit credentials
```

### 3. Run Development Mode

```bash
python main.py dev
```

The worker will connect to LiveKit Cloud and wait for room assignments.

### 4. Test with Web Call

1. Open frontend: `http://localhost:3000`
2. Login as a tenant
3. Go to `/dashboard/voice-agent/test`
4. Click "Start Call"
5. Speak to test the agent

## How It Works

### Architecture

```
User clicks "Start Call"
    ↓
Frontend calls: POST /voice-agent/webrtc/test
    ↓
Backend creates LiveKit room with metadata: {tenant_id: "123"}
    ↓
Agent worker receives job request
    ↓
Agent reads tenant_id from room metadata
    ↓
Agent calls: GET /voice-agent/tenant-config/123
    ↓
Agent receives: {api_keys, agent_config, business_name}
    ↓
Agent initializes LLM/TTS with tenant's API keys
    ↓
Agent joins room and responds with tenant's system prompt
```

### Tenant Isolation

Each room gets isolated configuration:
- **System Prompt**: "You are a dentist receptionist" vs "You are a lawyer receptionist"
- **API Keys**: Tenant A uses their Groq key, Tenant B uses different key
- **Voice**: Different voice IDs per tenant
- **LLM Model**: GPT-4 vs Claude vs Llama

### Function Tools

The agent has built-in tools that call your backend:

1. **check_appointment_availability(date, service_name)**
   - Calls: `GET /appointments/availability/check`
   - Returns available time slots

2. **book_appointment(customer_name, phone, email, service, date, time)**
   - Calls: `POST /appointments/`
   - Triggers N8N webhook if configured
   - Returns confirmation

3. **get_business_hours()**
   - Calls: `GET /admin/config`
   - Returns operating hours

4. **list_services()**
   - Calls: `GET /services/`
   - Returns available services

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LIVEKIT_URL` | LiveKit server URL | `wss://your-server.livekit.cloud` |
| `LIVEKIT_API_KEY` | LiveKit API key | `APIxxx...` |
| `LIVEKIT_API_SECRET` | LiveKit API secret | `xxx...` |
| `BACKEND_URL` | Backend API URL | `http://localhost:8000` |
| `LOG_LEVEL` | Logging level (optional) | `INFO` or `DEBUG` |

## Production Deployment

### Option 1: Systemd Service (Linux)

1. Copy files to server:
```bash
scp -r livekit-agent-worker user@server:/opt/callflow-agent
```

2. Create systemd service:
```bash
sudo nano /etc/systemd/system/callflow-agent.service
```

Paste:
```ini
[Unit]
Description=CallFlow AI Multi-Tenant Agent Worker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/callflow-agent
Environment="PATH=/opt/callflow-agent/venv/bin"
ExecStart=/opt/callflow-agent/venv/bin/python main.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start callflow-agent
sudo systemctl enable callflow-agent
```

4. Check status:
```bash
sudo systemctl status callflow-agent
sudo journalctl -u callflow-agent -f
```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "start"]
```

Build and run:
```bash
docker build -t callflow-agent .
docker run -d --name callflow-agent --env-file .env callflow-agent
```

### Option 3: PM2 (Node.js)

```bash
pm2 start main.py --name callflow-agent --interpreter python
pm2 save
pm2 startup
```

## Monitoring

### Check Logs

Development:
```bash
# Console output shows all logs
python main.py dev
```

Production:
```bash
# Systemd
sudo journalctl -u callflow-agent -f

# Docker
docker logs -f callflow-agent

# PM2
pm2 logs callflow-agent
```

### Health Check

The worker automatically reports health to LiveKit. Check LiveKit dashboard for:
- Worker status (online/offline)
- Active sessions
- Error rates

## Troubleshooting

### Agent Not Responding

**Check:** Agent worker logs
```bash
sudo journalctl -u callflow-agent -n 100
```

**Common Issues:**
- ❌ No tenant_id in room metadata → Check backend modification
- ❌ Can't fetch tenant config → Check BACKEND_URL
- ❌ No API keys → Tenant needs to add keys at `/settings/api-keys`

### Backend Connection Errors

**Check:** Backend is reachable
```bash
curl http://localhost:8000/voice-agent/tenant-config/test
```

**Fix:** Update `BACKEND_URL` in `.env`

### LiveKit Connection Issues

**Check:** LiveKit credentials
```bash
curl -X POST https://your-server.livekit.cloud
```

**Fix:** Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`

### Python Version Issues

**Requirements:** Python 3.10 or higher

```bash
python --version  # Should be 3.10+
```

## Testing

### Test with Different Tenants

1. **Create Tenant A (Dentist):**
   - Register account: dentist@example.com
   - Add Groq API key
   - System prompt: "You are a receptionist at Dr. Smith's dental office"
   - Test call: Ask "Do you have appointments tomorrow?"

2. **Create Tenant B (Lawyer):**
   - Register account: lawyer@example.com
   - Add different Groq API key
   - System prompt: "You are a receptionist at Johnson & Associates law firm"
   - Test call: Ask "Do you handle divorce cases?"

3. **Verify Isolation:**
   - Each agent responds with their specific context
   - API keys are not shared between tenants
   - Conversation histories are separate

## Development

### Adding New Function Tools

Edit `tenant_agent.py`:

```python
@function_tool
async def my_new_tool(
    self,
    ctx: RunContext[TenantContext],
    param1: str,
    param2: int,
) -> str:
    """
    Tool description for the LLM.
    
    Args:
        param1: Description
        param2: Description
    """
    # Your logic here
    return "Response to LLM"
```

The LLM will automatically discover and use the new tool.

### Changing LLM/TTS Providers

Edit `initialize_tenant_agent()` in `tenant_agent.py`:

```python
# Use different LLM
from livekit.plugins import anthropic
llm = anthropic.LLM(model="claude-3-5-sonnet-20241022", api_key=api_keys["anthropic"])

# Use different TTS
from livekit.plugins import openai
tts = openai.TTS(voice="alloy")
```

## Support

**Documentation:** See main project README  
**Issues:** Check `IMPLEMENTATION_CHECKLIST.md` for troubleshooting  
**Logs:** Always check worker logs first when debugging

## License

Part of CallFlow AI platform. See main project license.
