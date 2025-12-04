# N8N Workflows - Enhanced Setup Guide

## Overview
This directory contains n8n automation workflows for the AI Receptionist platform. These workflows handle appointment lifecycle, customer communications, and business intelligence.

## Workflows

### 1. **01_appointment_lifecycle_enhanced.json** 🌟 RECOMMENDED
**Enhanced version with smart features**

**What it does:**
1. ✅ Checks customer history (returning customer detection)
2. ✅ Checks Google Calendar for real-time conflicts
3. ✅ Checks database for double-booking prevention
4. ✅ Analyzes all data and makes smart decisions
5. ✅ Adds to Google Calendar with customer context
6. ✅ Sends personalized WhatsApp messages
7. ✅ Updates appointment metadata
8. ✅ Alerts owner if conflicts detected

**Personalization Features:**
- Returning customers: "Welcome back Jane! Your 3rd visit with us 🎉"
- New customers: Standard professional confirmation
- Calendar events tagged with "RETURNING CUSTOMER" and visit count
- Last visit date shown in calendar description

**Conflict Handling:**
- If slot unavailable → Doesn't book, alerts owner with conflict details
- If slot available → Books and sends confirmations

**Webhook URL:** `http://localhost:5678/webhook/appointment-action`

**Required Credentials:**
- MongoDB connection (global-mongodb)
- Google Calendar OAuth2 (tenant-specific)
- WhatsApp Business API token (tenant-specific)

---

### 2. **01_appointment_lifecycle.json**
**Original/legacy version**

**What it does:**
1. Adds appointment to Google Calendar
2. Sends WhatsApp confirmation
3. Logs to Airtable (if configured)

**Webhook URL:** `http://localhost:5678/webhook/appointment-action`

**When to use:** Simple deployments without customer history tracking

---

### 3. **02_call_transcript_processor.json**
**AI-powered call analysis**

**What it does:**
1. Receives call transcript from Vapi
2. Analyzes with Groq AI (free tier)
3. Extracts:
   - Sentiment (positive/negative/neutral)
   - Action items
   - Call quality score
   - Booking success/failure
4. Sends Slack notification to owner
5. Logs to MongoDB for analytics

**Webhook URL:** `http://localhost:5678/webhook/livekit-call-ended`

**AI Model:** llama-3.1-70b-versatile (via Groq)

---

### 4. **03_whatsapp_reminders.json**
**Automated appointment reminders**

**What it does:**
1. Runs every hour (schedule trigger)
2. Finds appointments in next 60-75 minutes
3. Sends WhatsApp reminder to customer
4. Marks reminder_sent = true in database

**Schedule:** Every hour at :00
**Message Format:** "⏰ Reminder: Your [service] appointment is in 1 hour at [time]"

---

### 5. **04_owner_low_credit_alerts.json**
**Platform credit monitoring**

**What it does:**
1. Checks tenant credits every 6 hours
2. If credits < 100 → Send alert
3. Sends notification via:
   - Email
   - Slack (if configured)
   - SMS (optional)

**Schedule:** Every 6 hours
**Threshold:** 100 credits

---

## Setup Instructions

### Step 1: Import Workflows
```bash
# Start n8n
docker-compose up -d n8n

# Access n8n UI
# http://localhost:5678

# For each workflow:
# 1. Click "Import from File"
# 2. Select the .json file
# 3. Click "Import"
```

### Step 2: Configure Credentials

#### MongoDB Connection
```
Name: global-mongodb
Type: MongoDB
Connection: mongodb://mongodb:27017
Database: callflow_ai_saas
```

#### Google Calendar OAuth2 (Per Tenant)
```
Type: Google Calendar OAuth2
Redirect URL: http://localhost:5678/rest/oauth2-credential/callback
Scopes: https://www.googleapis.com/auth/calendar
```

#### WhatsApp Business API
```
Type: HTTP Header Auth
Header: Authorization
Value: Bearer YOUR_WHATSAPP_TOKEN
```

#### Groq API (for AI analysis)
```
Type: HTTP Header Auth
Header: Authorization
Value: Bearer YOUR_GROQ_API_KEY
```

### Step 3: Activate Workflows
For each workflow:
1. Open the workflow
2. Click "Active" toggle (top right)
3. Verify green checkmark appears

### Step 4: Configure Backend
Update `.env` file:
```bash
# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook

# Use enhanced workflow (recommended)
N8N_ENHANCED_WORKFLOW=appointment-action

# OR use legacy workflow
# N8N_ENHANCED_WORKFLOW=appointment-action-legacy
```

### Step 5: Test Workflows

#### Test Enhanced Appointment Flow
```bash
curl -X POST http://localhost:5678/webhook/appointment-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "tenant_id": "test_tenant_123",
    "appointment": {
      "client_name": "Jane Doe",
      "client_phone": "+15551234567",
      "datetime": "2025-12-03T14:00:00Z",
      "service": "Haircut",
      "duration_minutes": 30,
      "notes": "First time customer"
    }
  }'
```

Expected Response:
```json
{
  "success": true,
  "slot_available": true,
  "is_returning_customer": false,
  "actions_taken": [
    "Google Calendar: Added",
    "WhatsApp: Sent",
    "Metadata: Updated"
  ]
}
```

#### Test with Returning Customer
```bash
# Book once
curl -X POST ...

# Book again with same phone number
curl -X POST ... \
  -d '{"appointment": {"client_phone": "+15551234567", ...}}'
```

Expected: Personalized WhatsApp message + "RETURNING CUSTOMER" tag

---

## Monitoring & Troubleshooting

### View Execution Logs
1. Open n8n UI
2. Click "Executions" (left sidebar)
3. Filter by workflow
4. Click execution to see detailed logs

### Common Issues

#### ❌ "MongoDB connection failed"
**Solution:** Check MongoDB is running
```bash
docker-compose ps mongodb
docker-compose logs mongodb
```

#### ❌ "Google Calendar authentication failed"
**Solution:** Re-authenticate
1. Go to Credentials
2. Click "Google Calendar OAuth2"
3. Click "Reconnect"
4. Authorize with Google

#### ❌ "WhatsApp message not sent"
**Solution:** Verify token and phone number ID
```bash
# Test WhatsApp API directly
curl -X POST https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"messaging_product": "whatsapp", "to": "15551234567", "type": "text", "text": {"body": "Test"}}'
```

#### ❌ "Workflow execution timeout"
**Solution:** Increase timeout in workflow settings
1. Open workflow
2. Click Settings (gear icon)
3. Set "Execution Timeout" to 300 seconds

### Performance Tips

1. **Use Enhanced Workflow for < 1000 appointments/day**
   - Real-time checks are fast enough
   - Better customer experience

2. **Use Legacy Workflow for > 1000 appointments/day**
   - Skip history/calendar checks
   - Faster execution
   - Post-process conflicts separately

3. **Enable Workflow Caching**
   - Stores tenant configs in memory
   - Reduces database queries

---

## Environment Variables

Backend recognizes these n8n-related variables:

```bash
# n8n webhook base URL
N8N_WEBHOOK_URL=http://localhost:5678/webhook

# Which appointment workflow to use
N8N_ENHANCED_WORKFLOW=appointment-action  # Enhanced with history checks
# or
N8N_ENHANCED_WORKFLOW=appointment-action-legacy  # Simple version

# Groq API for call analysis
GROQ_API_KEY=REDACTED

# WhatsApp Business API
WHATSAPP_TOKEN=REDACTED
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

---

## Workflow Selection Guide

| Feature | Enhanced | Legacy |
|---------|----------|--------|
| Customer history tracking | ✅ | ❌ |
| Calendar conflict checking | ✅ | ❌ |
| Personalized messages | ✅ | ❌ |
| Double-booking prevention | ✅ | ❌ |
| Execution time | ~3-5s | ~1-2s |
| Database queries | 3 | 0 |
| Best for | < 1000/day | > 1000/day |

**Recommendation:** Start with Enhanced, switch to Legacy only if performance becomes an issue.

---

## Adding Custom Workflows

### Template Structure
```json
{
  "name": "Your Workflow Name",
  "nodes": [
    {
      "parameters": {...},
      "id": "unique-node-id",
      "name": "Node Display Name",
      "type": "n8n-nodes-base.webhook",
      "position": [x, y]
    }
  ],
  "connections": {...}
}
```

### Best Practices
1. Use webhook triggers for real-time processing
2. Use schedule triggers for periodic tasks
3. Add error handling nodes (IF node + Set node)
4. Log to MongoDB for audit trail
5. Keep workflows under 20 nodes for maintainability

---

## Support

**Documentation:** https://docs.n8n.io
**Community:** https://community.n8n.io
**GitHub:** https://github.com/n8n-io/n8n

**Project Issues:** See main README.md for support channels
