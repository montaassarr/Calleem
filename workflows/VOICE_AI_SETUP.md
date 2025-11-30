# Voice AI Setup Guide

## Overview
This guide explains how to connect **VAPI** or **ElevenLabs** to your n8n workflows for voice-based appointment booking.

---

## Step 1: Import n8n Workflows

1. Access your n8n instance at `http://localhost:5678`
2. Login with credentials from `.env` file
3. Import the following workflows:
   - `get_available_slots.json`
   - `book_appointment.json`
   - (Optional) `update_appointment.json`
   - (Optional) `cancel_appointment.json`

4. **Activate** each workflow to generate webhook URLs

---

## Step 2: Configure Your Tenant

### Via Dashboard (Recommended)
1. Login to your dashboard at `http://localhost:3000`
2. Navigate to **Settings → API Keys**
3. Enter your API keys:
   - **OpenAI API Key** (for LLM)
   - **VAPI Private Key** OR **ElevenLabs API Key**
   - **Twilio Account SID** (if using phone calls)
   - **Twilio Auth Token**
   - **Twilio Phone Number**

### Via API (Alternative)
```bash
curl -X PUT http://localhost:8000/api/v1/tenants/me/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "openai_key": "sk-...",
    "vapi_private_key": "...",
    "twilio_account_sid": "AC...",
    "twilio_auth_token": "...",
    "twilio_phone_number": "+1234567890"
  }'
```

---

## Step 3A: Configure VAPI

### 1. Create VAPI Assistant
- Go to [VAPI Dashboard](https://vapi.ai)
- Create a new Assistant
- Set **Model**: `gpt-4` or `gpt-3.5-turbo`

### 2. System Prompt
```
You are a friendly AI receptionist for [BUSINESS_NAME]. Your job is to help customers:
1. Check available appointment slots
2. Book new appointments
3. Reschedule existing appointments
4. Cancel appointments

Always be polite and confirm details before booking.
```

### 3. Add Tools
Copy the **Production Webhook URLs** from your n8n workflows:

#### Tool 1: Check Availability
- **Name**: `getslots`
- **Description**: "Check available appointment slots"
- **Webhook URL**: `https://your-n8n-url.com/webhook/getslots`
- **Parameters**:
  ```json
  {
    "starttime": "ISO 8601 datetime",
    "endtime": "ISO 8601 datetime"
  }
  ```

#### Tool 2: Book Appointment
- **Name**: `bookslots`
- **Description**: "Book a new appointment"
- **Webhook URL**: `https://your-n8n-url.com/webhook/bookslots`
- **Parameters**:
  ```json
  {
    "email": "string",
    "name": "string",
    "notes": "string",
    "starttime": "ISO 8601 datetime"
  }
  ```

### 4. Test Your Assistant
- Call your VAPI phone number
- Try: "I'd like to book an appointment for tomorrow at 2 PM"

---

## Step 3B: Configure ElevenLabs

### 1. Create Conversational AI Agent
- Go to [ElevenLabs Dashboard](https://elevenlabs.io)
- Navigate to **Conversational AI**
- Create a new Agent

### 2. Agent Configuration
- **Voice**: Select your preferred voice
- **LLM**: Choose GPT-4 or GPT-3.5-turbo
- **System Prompt**: (Same as VAPI above)

### 3. Add Webhooks
In the **Tools** section, add:

#### Webhook 1: Get Slots
- **Name**: `check_availability`
- **URL**: `https://your-n8n-url.com/webhook/getslots`
- **Method**: POST
- **Body**:
  ```json
  {
    "customer_phone": "{{caller_phone}}",
    "start_time": "{{start_time}}",
    "end_time": "{{end_time}}",
    "tool_call_id": "{{tool_call_id}}"
  }
  ```

#### Webhook 2: Book Appointment
- **Name**: `book_appointment`
- **URL**: `https://your-n8n-url.com/webhook/bookslots`
- **Method**: POST
- **Body**:
  ```json
  {
    "customer_phone": "{{caller_phone}}",
    "email": "{{email}}",
    "name": "{{name}}",
    "notes": "{{notes}}",
    "starttime": "{{starttime}}",
    "tool_call_id": "{{tool_call_id}}"
  }
  ```

### 4. Test Your Agent
- Use the ElevenLabs test interface
- Try a booking conversation

---

## Step 4: Expose n8n Webhooks (Production)

### Option A: ngrok (Quick Testing)
```bash
ngrok http 5678
# Copy the HTTPS URL and update VAPI/ElevenLabs webhook URLs
```

### Option B: Reverse Proxy (Production)
Add to your `nginx.conf`:
```nginx
location /webhook/ {
    proxy_pass http://localhost:5678/webhook/;
    proxy_set_header Host $host;
}
```

---

## Troubleshooting

### "Tenant not found" Error
- Ensure your phone number is saved in the tenant config
- Check: `GET /api/v1/tenants/me` returns your phone number

### "API Key Invalid" Error
- Verify API keys are correctly entered in dashboard
- Check encryption is working: `docker-compose logs core-service`

### Webhook Not Triggering
- Ensure n8n workflows are **activated**
- Check n8n logs: `docker-compose logs n8n`
- Verify webhook URL is publicly accessible

---

## Next Steps
- Add more tools (update, cancel appointments)
- Customize system prompts for your business
- Set up call recording and analytics
