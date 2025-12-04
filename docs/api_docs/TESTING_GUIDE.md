# Quick Start Testing Guide

## Prerequisites
- Docker and Docker Compose installed
- Ports 3000, 5678, 8000, 27017 available

## Step 1: Start the Stack

```bash
cd /home/montassar/Desktop/ai_receptionist/infrastructure
docker-compose up -d
```

**Wait for services to be healthy** (~30 seconds):
```bash
docker-compose ps
```

All services should show "healthy" status.

## Step 2: Access Services

- **Frontend**: http://localhost:3000
- **n8n**: http://localhost:5678 (admin/password from .env)
- **Core API**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## Step 3: Create Your First Tenant

### Via Frontend
1. Go to http://localhost:3000/signup
2. Fill in:
   - **Email**: your@email.com
   - **Username**: testuser
   - **Password**: Test123!
   - **Full Name**: Test User
   - **Business Name**: My Barber Shop
   - **Phone**: +1234567890

3. Click **Sign Up**
4. Login with your credentials

### Verify Tenant Creation
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Step 4: Configure API Keys

1. Login to dashboard
2. Navigate to **Settings → API Keys**
3. Enter your keys:
   - **OpenAI API Key**: sk-...
   - **VAPI Private Key**: (optional)
   - **ElevenLabs API Key**: (optional)
   - **Twilio Account SID**: AC...
   - **Twilio Auth Token**: ...
   - **Twilio Phone Number**: +1234567890

4. Click **Save API Keys**

## Step 5: Import n8n Workflows

1. Access n8n at http://localhost:5678
2. Login (credentials from `.env`)
3. Click **+ Add Workflow**
4. Click **⋮** → **Import from File**
5. Import each workflow:
   - `workflows/get_available_slots.json`
   - `workflows/book_appointment.json`
   - `workflows/update_appointment.json`
   - `workflows/cancel_appointment.json`

6. **Activate** each workflow (toggle switch in top right)

## Step 6: Get Webhook URLs

For each activated workflow:
1. Click on the **Webhook Trigger** node
2. Copy the **Production URL**
3. Note it down for VAPI/ElevenLabs configuration

Example URLs:
- Get Slots: `http://localhost:5678/webhook/getslots`
- Book: `http://localhost:5678/webhook/bookslots`
- Update: `http://localhost:5678/webhook/updateslots`
- Cancel: `http://localhost:5678/webhook/cancelslots`

## Step 7: Test Core API Endpoints

### Test Tenant Lookup
```bash
curl -X POST http://localhost:8000/api/v1/tenants/lookup-by-phone \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

Expected: Returns tenant_id and decrypted API keys

### Test Appointment Creation
```bash
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -d '{
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "client_phone": "+1234567890",
    "datetime": "2025-12-01T14:00:00Z",
    "duration": 30,
    "service_id": "default"
  }'
```

## Step 8: Test n8n Workflow

```bash
curl -X POST http://localhost:5678/webhook/getslots \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "message": {
        "call": {
          "customer": {
            "number": "+1234567890"
          }
        },
        "toolCalls": [{
          "id": "test-123",
          "function": {
            "arguments": {
              "starttime": "2025-12-01T09:00:00Z",
              "endtime": "2025-12-01T18:00:00Z"
            }
          }
        }]
      }
    }
  }'
```

Expected: Returns available time slots

## Step 9: Configure VAPI (Optional)

See `workflows/VOICE_AI_SETUP.md` for detailed VAPI/ElevenLabs configuration.

## Troubleshooting

### Core Service Won't Start
```bash
docker-compose logs core-service
```
Check for missing dependencies or MongoDB connection issues.

### n8n Workflow Fails
1. Check n8n execution logs (click on workflow execution)
2. Verify Core Service is running: `curl http://localhost:8000/health`
3. Ensure tenant phone number matches

### API Keys Not Saving
1. Check browser console for errors
2. Verify JWT token is valid
3. Check Core Service logs for encryption errors

## Next Steps
- Configure VAPI or ElevenLabs
- Test voice call flow
- Deploy to production (see deployment docs)
