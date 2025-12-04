# 🎯 N8N IMPLEMENTATION QUICK START

This is your **action plan** to get n8n running in production with CallFlow AI.

---

## ⚡ 30-Minute Quick Start

### Step 1: Deploy n8n (10 minutes)

```bash
# Navigate to your project
cd /home/montassar/Desktop/ai_receptionist

# Create docker-compose for n8n
cat > docker-compose.n8n.yml <<EOF
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: callflow-n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=YourSecurePassword123!
      - N8N_HOST=localhost
      - N8N_PROTOCOL=http
      - N8N_PORT=5678
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/Los_Angeles
      - N8N_LOG_LEVEL=info
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - ai_receptionist_network

volumes:
  n8n_data:

networks:
  ai_receptionist_network:
    external: true
EOF

# Start n8n
docker-compose -f docker-compose.n8n.yml up -d

# Check logs
docker logs -f callflow-n8n
```

Open: http://localhost:5678  
Login: `admin` / `YourSecurePassword123!`

---

### Step 2: Configure MongoDB Connection (5 minutes)

1. In n8n dashboard: **Settings** → **Credentials** → **Add Credential**
2. Search for: `MongoDB`
3. Fill in:
   - **Connection Type:** Database Connection
   - **Database:** `ai_barber_receptionist` (or your DB name)
   - **Connection String:** `mongodb://localhost:27017` (or your MongoDB URI)
4. Click **Create**
5. **Important:** Note the credential ID (e.g., `cred_abc123`)

---

### Step 3: Import Your First Workflow (5 minutes)

1. **Workflows** → **Add Workflow** → **Import from File**
2. Select: `n8n_workflows/01_appointment_lifecycle.json`
3. Click **Import**
4. Update MongoDB credential:
   - Click on any MongoDB node
   - Select the credential you created in Step 2
5. Click **Save**

---

### Step 4: Get Webhook URL (2 minutes)

1. Click on **"Webhook Trigger"** node
2. Copy the URL (e.g., `http://localhost:5678/webhook/appointment-action`)
3. Save this URL — you'll need it for FastAPI integration

---

### Step 5: Test the Workflow (5 minutes)

```bash
# Test from terminal
curl -X POST http://localhost:5678/webhook/appointment-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "tenant_id": "507f1f77bcf86cd799439011",
    "appointment": {
      "client_name": "Test User",
      "client_phone": "+1234567890",
      "datetime": "2025-12-15T10:00:00Z",
      "duration_minutes": 30,
      "service": "Test Haircut",
      "notes": "First test"
    }
  }'
```

**Expected result:** Workflow executes successfully (check Executions tab in n8n)

---

### Step 6: Activate Workflow (1 minute)

1. Click **"Active"** toggle (top right of workflow editor)
2. Workflow is now live! 🎉

---

## 🔗 Integrate with FastAPI Backend (15 minutes)

### Option A: Quick Integration (Recommended for Testing)

**File:** `backend/routers/appointments.py`

Add at the top:
```python
import httpx
import os

N8N_WEBHOOK_URL = os.getenv("N8N_APPOINTMENT_WEBHOOK", "http://localhost:5678/webhook/appointment-action")
```

Replace the WhatsApp confirmation logic (around line 108):
```python
# OLD CODE (comment out):
# try:
#     confirmation_msg = f"""✅ Appointment Confirmed! ..."""
#     whatsapp_cloud.send_text_message(client_phone, confirmation_msg)
# except Exception as e:
#     logger.warning(f"Failed to send WhatsApp confirmation: {e}")

# NEW CODE (n8n integration):
try:
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(N8N_WEBHOOK_URL, json={
            "action": "create",
            "tenant_id": tenant_id,
            "appointment": created_appointment
        })
    logger.info(f"✅ Triggered n8n workflow for appointment {created_appointment['id']}")
except Exception as e:
    logger.warning(f"Failed to trigger n8n workflow: {e}")
```

Add to `.env`:
```bash
N8N_APPOINTMENT_WEBHOOK=http://localhost:5678/webhook/appointment-action
```

**Test it:**
```bash
# Restart backend
cd backend
python main.py

# Create appointment via API (use Postman or curl)
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "datetime": "2025-12-15T10:00:00Z",
    "duration_minutes": 30,
    "service": "Haircut"
  }'
```

Check n8n **Executions** tab — you should see the workflow run!

---

### Option B: Full Integration (Production-Ready)

Create a new service file:

**File:** `backend/services/n8n_webhooks.py`

```python
"""
N8N Webhook Integration Service
Centralized service for triggering n8n workflows
"""

import httpx
import logging
from typing import Dict, Any, Optional
from utils.config import settings

logger = logging.getLogger(__name__)


class N8nWebhookService:
    """Service for triggering n8n workflows via webhooks"""
    
    def __init__(self):
        self.base_url = settings.N8N_WEBHOOK_BASE_URL or "http://localhost:5678"
        self.webhooks = {
            "appointment_lifecycle": f"{self.base_url}/webhook/appointment-action",
            "call_transcript": f"{self.base_url}/webhook/livekit-call-ended",
        }
    
    async def trigger_appointment_action(
        self, 
        action: str, 
        appointment: Dict[str, Any], 
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger appointment lifecycle workflow
        
        Args:
            action: "create", "update", or "cancel"
            appointment: Appointment data
            tenant_id: Tenant ID
            
        Returns:
            Workflow response or None if failed
        """
        webhook_url = self.webhooks["appointment_lifecycle"]
        
        payload = {
            "action": action,
            "tenant_id": tenant_id,
            "appointment": appointment
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                
                logger.info(f"✅ n8n workflow triggered: {action} appointment {appointment.get('id')}")
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"❌ Failed to trigger n8n workflow: {e}")
            return None
    
    async def trigger_call_ended(
        self,
        call_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger call transcript processing workflow
        
        Args:
            call_data: Vapi call-ended event data
            
        Returns:
            Workflow response or None if failed
        """
        webhook_url = self.webhooks["call_transcript"]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(webhook_url, json=call_data)
                response.raise_for_status()
                
                logger.info(f"✅ Call transcript workflow triggered: {call_data.get('call_id')}")
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"❌ Failed to trigger call transcript workflow: {e}")
            return None


# Singleton instance
n8n_webhooks = N8nWebhookService()
```

Update `backend/utils/config.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # N8N Configuration
    N8N_WEBHOOK_BASE_URL: str = "http://localhost:5678"
    N8N_API_URL: str = "http://localhost:5678/api/v1"
    N8N_API_KEY: str = ""
```

Use in your routers:
```python
from services.n8n_webhooks import n8n_webhooks

# In appointments.py
await n8n_webhooks.trigger_appointment_action("create", created_appointment, tenant_id)

# In voice_agent.py (for Vapi webhooks)
await n8n_webhooks.trigger_call_ended(call_data)
```

---

## 📊 Setup Credentials for Other Services

### Google Calendar OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth2 credentials
3. Add redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
4. In n8n: **Credentials** → **Google Calendar OAuth2 API**
5. Enter Client ID & Secret
6. Click **Connect** → Authorize

### OpenAI API

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. In n8n: **Credentials** → **OpenAI API**
3. Enter API Key
4. Test connection

### WhatsApp Cloud API

**Note:** Already configured in your backend. n8n uses HTTP Request node with Bearer token from tenant config.

### Airtable

1. Get Personal Access Token from [Airtable](https://airtable.com/create/tokens)
2. In n8n: **Credentials** → **Airtable Personal Access Token API**
3. Enter token
4. Test connection

---

## 🧪 Testing Checklist

- [ ] n8n container running (`docker ps`)
- [ ] Can access dashboard (http://localhost:5678)
- [ ] MongoDB credential configured
- [ ] Appointment workflow imported
- [ ] Webhook URL obtained
- [ ] Test webhook with curl (successful)
- [ ] Workflow activated
- [ ] FastAPI integration added
- [ ] End-to-end test (create appointment via API)
- [ ] Check n8n execution log (success)
- [ ] Verify WhatsApp sent (if enabled)

---

## 🚀 Deploy to Production

### Update docker-compose.n8n.yml:

```yaml
environment:
  - N8N_HOST=n8n.yourdomain.com
  - N8N_PROTOCOL=https
  - WEBHOOK_URL=https://n8n.yourdomain.com/
```

### Add Nginx reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name n8n.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/n8n.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Update backend .env:

```bash
N8N_WEBHOOK_BASE_URL=https://n8n.yourdomain.com
```

---

## 📈 Monitor & Scale

### View Workflow Executions

- n8n Dashboard → **Executions**
- Filter by workflow name
- View input/output for each execution
- Check for errors

### Set Retention Policy

In docker-compose.n8n.yml:
```yaml
- EXECUTIONS_DATA_PRUNE=true
- EXECUTIONS_DATA_MAX_AGE=168  # 7 days
```

### Enable Error Workflows

Create a separate workflow:
- **Trigger:** Error Trigger
- **Action:** Send email/Telegram to you when any workflow fails

---

## 🆘 Common Issues

### "Webhook not found"
**Fix:** Ensure workflow is **Active** (toggle in top right)

### "MongoDB connection failed"
**Fix:** Check connection string in credential settings

### "Timeout error"
**Fix:** Increase timeout in httpx.AsyncClient(timeout=30.0)

### "WhatsApp not sending"
**Fix:** Verify WhatsApp token in tenant config (not expired)

---

## 🎯 Next Steps

1. ✅ Complete this quick start
2. Import remaining workflows:
   - `02_call_transcript_processor.json`
   - `03_whatsapp_reminders.json`
   - `04_owner_low_credit_alerts.json`
3. Configure Google Calendar OAuth
4. Set up Telegram bot for owner alerts
5. Build dashboard automations toggle page
6. Roll out to pilot tenant
7. Monitor for 48 hours
8. Roll out to all tenants

---

**Questions?** Check the main `N8N_TAKEOVER_BLUEPRINT.md` for architecture details.

**Ready to scale?** See `n8n_workflows/README.md` for all workflows.
