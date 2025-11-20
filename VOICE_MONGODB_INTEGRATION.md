# Voice Agent MongoDB Integration - Complete Guide

## 🎯 Overview

Your AI Voice Agent (Vapi) is now **fully integrated** with MongoDB using the **same booking logic and database workflow** as your WhatsApp text agent. Both agents now share:

- ✅ **Same MongoDB collections** with normalized schemas
- ✅ **Same booking validation logic**
- ✅ **Same availability checking**
- ✅ **Same appointment creation/update/cancel flows**
- ✅ **Unified conversation history** (tagged as "voice" or "text")

---

## 📊 Normalized MongoDB Schema

### Collections (KEEP ONLY THESE 5):

1. **appointments** - All bookings from voice and text
2. **availability** - Business hours per day of week  
3. **services** - Available services with pricing
4. **business_config** - Business settings and configuration
5. **conversation_history** - All messages (voice + text)

### Schema Details:

#### `appointments`
```javascript
{
  "_id": ObjectId,
  "businessId": "default",           // Tenant ID
  "name": "John Doe",                // Client name
  "phone": "+21692034689",           // Client phone (E.164)
  "service": "Haircut",              // Service name
  "start": ISODate("2025-11-20T10:00:00Z"),  // Start time
  "end": ISODate("2025-11-20T10:30:00Z"),    // End time
  "notes": "Prefers fade",           // Optional notes
  "source": "voice",                 // "voice" or "text"
  "status": "confirmed",             // confirmed, cancelled, completed
  "createdAt": ISODate,
  "updatedAt": ISODate
}
```

#### `availability`
```javascript
{
  "_id": ObjectId,
  "businessId": "default",
  "dayOfWeek": 0,                    // 0=Monday, 6=Sunday
  "open": "09:00",                   // Opening time HH:MM
  "close": "20:00",                  // Closing time HH:MM
  "breaks": [                        // Break periods
    {"start": "13:00", "end": "14:00"}
  ],
  "isOpen": true                     // Is business open this day
}
```

#### `services`
```javascript
{
  "_id": ObjectId,
  "businessId": "default",
  "name": "Haircut",
  "durationMinutes": 30,
  "price": 25.0,
  "isActive": true
}
```

#### `business_config`
```javascript
{
  "_id": ObjectId,
  "businessId": "default",
  "name": "Royal Fade Barbershop",
  "phone": "+21692034689",
  "timezone": "Africa/Tunis",
  "openingHours": [...],             // Reference to availability
  "services": [...],                 // Reference to services
  "features": {
    "voiceAgent": true
  },
  "voiceConfig": {...},
  "aiConfig": {...}
}
```

#### `conversation_history`
```javascript
{
  "_id": ObjectId,
  "businessId": "default",
  "type": "voice",                   // "voice" or "text"
  "sender": "client",                // "client" or "agent"
  "message": "I want to book a haircut",
  "timestamp": ISODate,
  "metadata": {
    "callId": "call_abc123",         // For voice calls
    "phone": "+21692034689",
    "service": "Haircut",
    "appointmentId": "..."
  }
}
```

---

## 🚀 Migration Instructions

### Step 1: Backup Your Database (IMPORTANT!)

```powershell
# Export your current MongoDB data
mongodump --uri="your_mongodb_uri" --out=backup_before_migration
```

### Step 2: Run the Migration Script

```powershell
# Navigate to backend directory
cd backend

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Run migration
python migrate_to_normalized_schema.py
```

The migration script will:
1. ✅ Convert all appointments to normalized schema (start/end, phone, name)
2. ✅ Extract services from business_config to dedicated collection
3. ✅ Extract availability from business_config to dedicated collection
4. ✅ Normalize business_config field names
5. ✅ Create conversation_history from existing conversations
6. ✅ Optionally clean up old collections

### Step 3: Verify Migration

```powershell
# Check MongoDB collections
python check_db.py
```

Expected output:
```
✅ Collections found:
  - appointments: X documents
  - availability: Y documents  
  - services: Z documents
  - business_config: 1 document
  - conversation_history: W documents
```

---

## 🔧 What Changed

### Voice Agent Tools (`backend/voice_agent/tools.py`)

**Before:**
```python
# OLD - Using inconsistent field names
{
  "business_id": "default",
  "client_name": "John",
  "client_phone": "+123...",
  "scheduled_time": datetime,
  "duration_minutes": 30
}
```

**After:**
```python
# NEW - Using normalized schema
{
  "businessId": "default",
  "name": "John",
  "phone": "+123...",
  "start": datetime,
  "end": datetime,
  "source": "voice"
}
```

### Conversation Manager (`backend/ai/conversation_manager.py`)

**Added:**
- ✅ Conversation history logging with type="voice" or "text"
- ✅ Normalized appointment creation (start/end instead of datetime)
- ✅ businessId tracking throughout the flow

### Key Functions Updated:

1. **`check_availability`** - Now uses `availability` collection with dayOfWeek, open, close
2. **`book_appointment`** - Creates appointments with start/end times, logs to conversation_history
3. **`update_appointment`** - Updates start/end times using normalized fields
4. **`cancel_appointment`** - Cancels using phone field, logs to conversation_history
5. **`get_services`** - Fetches from dedicated `services` collection

---

## 🧪 Testing the Integration

### Test 1: Voice Agent Availability Check

```bash
# In Vapi dashboard, start a test call and say:
"What times are available tomorrow?"

# Expected: Agent checks MongoDB availability collection
# Returns: Available slots based on dayOfWeek schedule
```

### Test 2: Voice Agent Booking

```bash
# In Vapi dashboard:
"I want to book a haircut for tomorrow at 2 PM"

# Expected: 
# 1. Creates appointment in MongoDB with source="voice"
# 2. Logs to conversation_history with type="voice"
# 3. Returns confirmation
```

### Test 3: WhatsApp Text Booking

```bash
# Send WhatsApp message:
"Book a haircut for tomorrow 3pm"

# Expected:
# 1. Creates appointment in MongoDB with source="text"
# 2. Logs to conversation_history with type="text"
# 3. Both agents see same appointments
```

### Test 4: Check Conversation History

```python
# In Python shell or check_db.py
from database.mongo_config import get_database
import asyncio

async def check():
    db = get_database()
    
    # Get all conversation history
    history = await db.conversation_history.find({}).to_list(length=100)
    
    voice_count = sum(1 for h in history if h['type'] == 'voice')
    text_count = sum(1 for h in history if h['type'] == 'text')
    
    print(f"Voice messages: {voice_count}")
    print(f"Text messages: {text_count}")

asyncio.run(check())
```

---

## 🎯 Benefits of This Integration

### 1. **No Temporary Memory**
- ❌ **REMOVED:** In-memory appointment storage
- ✅ **NOW:** All data persists in MongoDB immediately

### 2. **Unified Booking Logic**
- Voice and text agents use **identical** validation
- Both check **same availability** in MongoDB
- Both create appointments with **same schema**

### 3. **Complete Audit Trail**
- `conversation_history` tracks every interaction
- Tagged as "voice" or "text" for analytics
- Includes metadata (callId, phone, service, etc.)

### 4. **Multi-Tenant Ready**
- All collections use `businessId` field
- Easy to scale to multiple businesses
- Each tenant has isolated data

### 5. **Clean Database**
- Only 5 essential collections
- No duplicate data
- Consistent field naming across all collections

---

## 📋 Verification Checklist

After migration, verify:

- [ ] Migration script ran without errors
- [ ] All appointments have `start`, `end`, `phone`, `name` fields
- [ ] `availability` collection has 7 entries (one per day) per business
- [ ] `services` collection has your services list
- [ ] `conversation_history` has entries with type="voice" or "text"
- [ ] Voice agent can check availability
- [ ] Voice agent can book appointments
- [ ] Voice agent can update appointments
- [ ] Voice agent can cancel appointments
- [ ] WhatsApp agent still works (shares same DB)
- [ ] Dashboard shows all appointments from both sources

---

## 🔍 Troubleshooting

### Issue: Voice agent returns "Database unavailable"

**Solution:**
```python
# Check MongoDB connection
from database.mongo_config import get_database
db = get_database()
print("Connected" if db else "NOT CONNECTED")
```

### Issue: Appointments not showing in dashboard

**Solution:**
```javascript
// Check field names in MongoDB
db.appointments.findOne()

// Should show: start, end, name, phone (not datetime, client_name, etc.)
```

### Issue: Availability check returns "closed"

**Solution:**
```python
# Verify availability collection
import asyncio
from database.mongo_config import get_database

async def check():
    db = get_database()
    avail = await db.availability.find({"businessId": "default"}).to_list(7)
    for a in avail:
        print(f"Day {a['dayOfWeek']}: {a['open']}-{a['close']} (Open: {a['isOpen']})")

asyncio.run(check())
```

---

## 🚨 Important Notes

1. **Backup Before Migration**: Always backup your database first!
2. **Test in Dev First**: Run migration on a test database before production
3. **Monitor Logs**: Check `backend/logs/` for any errors during migration
4. **Verify All Fields**: Ensure all appointments have required fields (name, phone, start, end)
5. **Check businessId**: All documents should have businessId="default" (or your tenant ID)

---

## 📞 Support

If you encounter any issues:

1. Check logs in `backend/logs/`
2. Verify MongoDB connection
3. Run `python check_db.py` to see current state
4. Review migration script output for specific errors

---

## ✅ Success Criteria

You'll know the integration is successful when:

1. ✅ Migration script completes with 0 errors
2. ✅ Voice agent can book appointments in test mode
3. ✅ Appointments appear in MongoDB with normalized schema
4. ✅ Conversation history logs all voice interactions
5. ✅ WhatsApp agent and Voice agent share the same appointments
6. ✅ Dashboard shows appointments from both sources

---

## 🎉 Next Steps

After successful migration:

1. **Test thoroughly** in dashboard test mode
2. **Monitor** first few real voice bookings
3. **Verify** conversation history is logging correctly
4. **Clean up** old collections (migration script will prompt)
5. **Document** any custom business rules or configurations

---

**🔥 Your voice agent is now fully integrated with MongoDB using the EXACT same logic as your WhatsApp agent!**
