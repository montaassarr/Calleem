# 🔧 N8N Workflows for CallFlow AI

This directory contains ready-to-import n8n workflows for CallFlow AI automation.

## 📦 Available Workflows

### 1. **Appointment Lifecycle** (`01_appointment_lifecycle.json`)
**Purpose:** Automate appointment creation with multi-channel notifications

**Triggers:**
- Webhook: `POST /webhook/appointment-action`

**Features:**
- ✅ Google Calendar sync (if enabled)
- ✅ WhatsApp instant confirmation
- ✅ Airtable logging
- ✅ Conditional execution based on tenant settings

**Payload Example:**
```json
{
  "action": "create",
  "tenant_id": "507f1f77bcf86cd799439011",
  "appointment": {
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "client_email": "john@example.com",
    "datetime": "2025-12-15T10:00:00Z",
    "duration_minutes": 30,
    "service": "Haircut",
    "notes": "First time client"
  }
}
```

---

### 2. **Call Transcript Processor** (`02_call_transcript_processor.json`)
**Purpose:** AI-powered call analysis with multi-platform logging

**Triggers:**
- Webhook: `POST /webhook/livekit-call-ended`

**Features:**
- ✅ AI summarization (OpenAI GPT-4)
- ✅ Sentiment analysis (positive/neutral/negative)
- ✅ Intent detection (booking/inquiry/complaint)
- ✅ Action items extraction
- ✅ MongoDB logging
- ✅ Slack notifications (if enabled)
- ✅ Airtable logging (if enabled)

**Payload Example:**
```json
{
  "call_id": "call_abc123",
  "status": "ended",
  "duration_seconds": 180,
  "tenant_id": "507f1f77bcf86cd799439011",
  "customer": {
    "number": "+1234567890"
  },
  "transcript": [
    {"role": "assistant", "text": "Hello, how can I help you?"},
    {"role": "user", "text": "I need a haircut tomorrow at 3pm"}
  ]
}
```

**AI Output:**
```json
{
  "summary": "Customer requested a haircut appointment for tomorrow at 3pm. Booking was confirmed.",
  "sentiment": "positive",
  "intent": "booking",
  "action_items": ["Add to calendar", "Send confirmation"],
  "key_topics": ["haircut", "appointment", "scheduling"],
  "booking_made": true,
  "follow_up_needed": false
}
```

---

### 3. **WhatsApp Reminders** (`03_whatsapp_reminders.json`)
**Purpose:** Reduce no-shows with automated 1-hour reminders

**Triggers:**
- Schedule: Every hour (on the hour)

**Features:**
- ✅ Finds appointments in next 1-hour window
- ✅ Sends personalized WhatsApp reminder
- ✅ Marks reminder as sent (prevents duplicates)
- ✅ Respects tenant automation settings

**No payload needed** - runs automatically via schedule.

**Example Message:**
```
⏰ Reminder: Your appointment is in 45 minutes!

📅 Monday, December 15 at 3:00 PM
💇 Service: Haircut

See you soon! - Joe's Barbershop
```

---

## 🚀 Installation Instructions

### Prerequisites
1. ✅ n8n installed (Docker recommended)
2. ✅ MongoDB connection configured
3. ✅ Credentials set up:
   - Google Calendar OAuth2
   - OpenAI API Key
   - WhatsApp Cloud API Token
   - Airtable Personal Access Token
   - Slack API Token (optional)

### Step 1: Import Workflows

1. Open n8n dashboard
2. Click **"+ New Workflow"** → **"Import from File"**
3. Select a JSON file from this directory
4. Click **"Import"**

### Step 2: Configure Credentials

Each workflow requires certain credentials. Map them as follows:

**MongoDB** (global, used by all):
- Type: `MongoDB`
- Connection: `mongodb://localhost:27017`
- Database: `ai_receptionist`

**Google Calendar** (per tenant):
- Type: `googleCalendarOAuth2Api`
- Complete OAuth flow
- Store credential ID in tenant config: `google_credential_id`

**OpenAI** (per tenant or global):
- Type: `openAiApi`
- API Key: From tenant config or your master key

**WhatsApp** (per tenant):
- Type: None (uses HTTP Request with Bearer token)
- Token stored in tenant config: `whatsapp_token`
- Phone Number ID: `whatsapp_phone_number_id`

**Airtable** (per tenant):
- Type: `airtableTokenApi`
- Personal Access Token
- Store credential ID in tenant config: `airtable_credential_id`

### Step 3: Update Webhook URLs

1. Open each workflow
2. Click on **"Webhook Trigger"** node
3. Copy the webhook URL (e.g., `https://n8n.yourdomain.com/webhook/appointment-action`)
4. Add to your FastAPI backend:

```python
# In backend/services/n8n_service.py or similar

N8N_WEBHOOK_URLS = {
    "appointment_lifecycle": "https://n8n.yourdomain.com/webhook/appointment-action",
    "call_transcript": "https://n8n.yourdomain.com/webhook/livekit-call-ended",
    # Reminder workflow runs on schedule, no webhook needed
}
```

### Step 4: Activate Workflows

1. In n8n, click **"Active"** toggle (top right)
2. Workflow is now live and ready to receive webhooks

---

## 🔗 Integration with FastAPI Backend

### Modify Appointment Router

**File:** `backend/routers/appointments.py`

**Before:**
```python
# Manual WhatsApp sending
whatsapp_cloud.send_text_message(client_phone, confirmation_msg)
```

**After:**
```python
# Trigger n8n workflow instead
import httpx

async def trigger_n8n_appointment(action: str, appointment: dict, tenant_id: str):
    """Trigger n8n appointment workflow"""
    webhook_url = "https://n8n.yourdomain.com/webhook/appointment-action"
    
    payload = {
        "action": action,
        "tenant_id": tenant_id,
        "appointment": appointment
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)
        return response.json()

# In create_appointment function:
await trigger_n8n_appointment("create", appointment_dict, tenant_id)
```

### Integrate LiveKit Call Events

**File:** `backend/routers/webhook.py` or `backend/routers/voice_agent.py`

Add webhook handler for LiveKit call-complete events (use LiveKit webhooks or Parker_165 agent callback to POST transcripts here):

```python
@router.post("/livekit/call-ended")
async def livekit_call_ended(request: Request):
  """Forward LiveKit call-ended event to n8n for processing"""
    body = await request.json()
    
    # Forward to n8n
    webhook_url = "https://n8n.yourdomain.com/webhook/livekit-call-ended"
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=body)
    
    return {"success": True}
```

Point your LiveKit Agent (or Parker_165 callback) to:
```
https://your-backend.com/api/v1/webhook/livekit/call-ended
```

---

## 🎛️ Tenant Configuration Schema

Update `business_config` collection to include:

```json
{
  "tenant_id": "507f1f77bcf86cd799439011",
  "business_name": "Joe's Barbershop",
  "automations": {
    "google_calendar_sync": true,
    "airtable_logging": true,
    "whatsapp_confirmations": true,
    "whatsapp_reminders": true,
    "slack_notifications": false,
    "call_transcription": true
  },
  "whatsapp_phone_number_id": "123456789",
  "whatsapp_token": "EAAxxxxx",
  "google_credential_id": "cred_123",
  "airtable_credential_id": "cred_456",
  "airtable_base_id": "appXXXXXXXXXXXXXX",
  "slack_channel": "call-logs",
  "slack_credential_id": "cred_789"
}
```

---

## 🧪 Testing

### Test Appointment Workflow

```bash
curl -X POST https://n8n.yourdomain.com/webhook/appointment-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "tenant_id": "507f1f77bcf86cd799439011",
    "appointment": {
      "client_name": "Test User",
      "client_phone": "+1234567890",
      "datetime": "2025-12-15T10:00:00Z",
      "duration_minutes": 30,
      "service": "Test Service"
    }
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Appointment processed successfully",
  "actions_taken": [
    "Google Calendar: Added",
    "WhatsApp: Sent",
    "Airtable: Logged"
  ]
}
```

### Test Call Transcript Workflow

```bash
curl -X POST https://n8n.yourdomain.com/webhook/livekit-call-ended \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_call_123",
    "status": "ended",
    "duration_seconds": 120,
    "tenant_id": "507f1f77bcf86cd799439011",
    "customer": {
      "number": "+1234567890"
    },
    "transcript": [
      {"role": "assistant", "text": "Hello, how can I help you?"},
      {"role": "user", "text": "I need a haircut tomorrow at 3pm"}
    ]
  }'
```

---

## 📈 Monitoring

### View Workflow Executions

1. Go to n8n dashboard
2. Click **"Executions"** in left sidebar
3. Filter by workflow name
4. View success/failure status and logs

### Set Up Alerts (Optional)

Create a separate workflow:

**Workflow:** `error-notifications`
**Trigger:** Error Trigger (catches failed executions)
**Actions:**
1. Send email to admin
2. Post to Slack #alerts channel
3. Log to MongoDB error collection

---

## 🔒 Security Best Practices

1. ✅ **Use HTTPS** for all webhook URLs
2. ✅ **Validate tenant_id** in every workflow (prevent cross-tenant access)
3. ✅ **Store credentials encrypted** in n8n
4. ✅ **Use Basic Auth** on n8n dashboard (N8N_BASIC_AUTH_ACTIVE=true)
5. ✅ **Rotate API keys** quarterly
6. ✅ **Monitor failed executions** for suspicious activity

---

## 🆘 Troubleshooting

### Workflow Not Triggering

**Symptom:** Webhook called but workflow doesn't execute

**Solution:**
1. Check workflow is **Active** (toggle in top right)
2. Verify webhook URL matches exactly
3. Check n8n logs: `docker logs callflow-n8n`

### Credentials Not Working

**Symptom:** "Credentials not found" error

**Solution:**
1. Re-authenticate credential in n8n
2. Check credential ID matches tenant config
3. Test credential using "Test" button in n8n

### MongoDB Connection Issues

**Symptom:** "Connection refused" or "Timeout"

**Solution:**
1. Verify MongoDB is accessible from n8n container
2. Check connection string format
3. Ensure database name matches

---

## 🎯 Next Steps

1. Import all 3 workflows
2. Configure credentials
3. Test with 1 pilot tenant
4. Monitor for 24 hours
5. Roll out to remaining tenants
6. Build dashboard toggle page (see main blueprint)

---

**Questions?** Check the main N8N_TAKEOVER_BLUEPRINT.md for detailed architecture and additional workflows.
