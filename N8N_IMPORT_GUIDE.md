# 🚀 N8N Import Guide - AI Receptionist

## What to Import (Priority Order)

### 1️⃣ **REQUIRED: Simple Appointment Lifecycle** ⭐ (NO SETUP NEEDED)
**File**: `n8n_workflows/01_appointment_lifecycle_SIMPLE.json`

**Why**: 
- ✅ Works immediately (no MongoDB node needed)
- ✅ Uses your backend API for everything
- ✅ Checks customer history (returning customers)
- ✅ Prevents double-booking
- ✅ Sends personalized WhatsApp confirmations

**Import Steps**:
1. Open http://localhost:5678
2. Click "Workflows" → "Add workflow" → "Import from File"
3. Select: `01_appointment_lifecycle_SIMPLE.json`
4. Click **Activate** (top-right toggle)
5. **Done!** No credentials needed

---

### 2️⃣ **ADVANCED: Enhanced Lifecycle (Requires MongoDB Node)**
**File**: `n8n_workflows/01_appointment_lifecycle_enhanced.json`

**Only use if you want**:
- Direct MongoDB queries (faster)
- Direct Google Calendar API access

**Requires**: Installing MongoDB node in n8n
```bash
docker exec n8n npm install n8n-nodes-base-mongodb
docker restart n8n
```

---

### 3️⃣ **OPTIONAL: Call Transcript Processor**
**File**: `n8n_workflows/02_call_transcript_processor.json`

**Why**:
- AI analysis of call transcripts
- Sentiment detection
- Action items extraction
- Logs to MongoDB + Slack

**Import**: Same steps as above

---

### 4️⃣ **OPTIONAL: WhatsApp Reminders**
**File**: `n8n_workflows/03_whatsapp_reminders.json`

**Why**:
- Sends 24h reminder before appointments
- Automatic "reply 1 to confirm" flow

---

### 5️⃣ **OPTIONAL: Low Credit Alerts**
**File**: `n8n_workflows/04_owner_low_credit_alerts.json`

**Why**:
- Alerts business owners when credits low
- Prevents service interruption

---

## 🚀 QUICK START (3 Steps - 2 Minutes)

1. **Import workflow**:
   - Open http://localhost:5678
   - Click "+ Add workflow" → "Import from File"
   - Select: `n8n_workflows/01_appointment_lifecycle_SIMPLE.json`

2. **Activate**:
   - Toggle switch in top-right to **ON** (green)

3. **Test**:
   ```bash
   curl -X POST http://localhost:5678/webhook/appointment-action \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_id": "692eeedbed6e199193f8754d",
       "appointment": {
         "customer_name": "Test Customer",
         "customer_phone": "+1234567890",
         "customer_email": "test@example.com",
         "date": "2025-12-10",
         "time": "14:00",
         "service": "Haircut",
         "duration_minutes": 30
       }
     }'
   ```

**That's it!** No credentials, no setup needed.

---

## 🔑 Credentials Setup (After Import)

### For Enhanced Appointment Lifecycle:

1. **MongoDB** (Customer History Check)
   ```
   Connection: mongodb://localhost:27017
   Database: callflow_ai_saas
   Collection: appointments
   ```

2. **Google Calendar API** (Availability Check)
   - Go to: https://console.cloud.google.com
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Add to n8n: Settings → Credentials → Google Calendar

3. **WhatsApp Business API** (Confirmations)
   - Provider: Cloud API or Twilio
   - Add credentials in n8n

4. **HTTP Request Auth** (Backend API)
   - No auth needed (internal network)
   - URL: http://localhost:8000

---

## ✅ Activation Checklist

After importing **Simple Appointment Lifecycle**:

- [ ] Workflow imported
- [ ] Workflow activated (toggle ON)
- [ ] Backend running on port 8000
- [ ] Test webhook works

**No credentials needed!** Everything uses your backend API.

---

## 🎯 Quick Start (Minimum Setup)

**Just want to test?** 
1. Import `01_appointment_lifecycle_SIMPLE.json`
2. Activate workflow (toggle ON)
3. Done!

---

## 📊 How It Integrates

```
Customer calls → LiveKit → Your Backend → n8n Simple Workflow
                                          ↓
                    ┌─────────────────────┴─────────────────────┐
                    ↓                     ↓                     
            Check History        Check Availability         
         (Backend API)          (Backend API)         
                    ↓                     ↓                     
                    └─────────────────────┬─────────────────────┘
                                          ↓
                          Smart Decision: Book or Alert
                                          ↓
                    ┌─────────────────────┴─────────────────────┐
                    ↓                                           ↓
          Save to Database                           Send WhatsApp
       (Backend API)                            ("Welcome back! 3rd visit")
```

---

## ❌ What NOT to Import

**Ignore these** (already deleted):
- `/workflows/` folder - OLD architecture
- Any files not in `n8n_workflows/` folder

---

## 🆘 Troubleshooting

**"Workflow not triggering"**:
- Check workflow is activated (green toggle)
- Verify the webhook URL matches the one printed inside each JSON (LiveKit webhook endpoint varies per deployment)
- Check logs: `docker logs n8n`

**"MongoDB connection failed"**:
- Ensure MongoDB running: `sudo systemctl status mongod`
- Test connection: `mongosh callflow_ai_saas`

**"No WhatsApp sent"**:
- WhatsApp credential may be missing (workflow will still work, just skip WhatsApp)
- Check n8n execution logs

---

## 📝 Summary

**Import Priority**:
1. ✅ `01_appointment_lifecycle_SIMPLE.json` (MUST HAVE - NO SETUP)
2. ⚠️ `01_appointment_lifecycle_enhanced.json` (Advanced - needs MongoDB node)
3. ⚠️ `02_call_transcript_processor.json` (NICE TO HAVE)
4. ⚠️ `03_whatsapp_reminders.json` (NICE TO HAVE)
5. ⚠️ `04_owner_low_credit_alerts.json` (NICE TO HAVE)

**Start with #1, works immediately with zero setup!**
