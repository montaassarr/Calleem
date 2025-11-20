# 🚀 Quick Start: Voice Agent MongoDB Integration

## Step-by-Step Instructions

### 1️⃣ **Backup Your Database** (5 minutes)

```powershell
# Create backup directory
mkdir mongodb_backup

# Export current database (if using MongoDB Atlas, download from web UI)
# If using local MongoDB:
mongodump --uri="mongodb://localhost:27017/ai_receptionist" --out=mongodb_backup
```

### 2️⃣ **Run Schema Verification** (2 minutes)

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Check current schema state
python verify_schema.py
```

**Expected Output:**
```
====================================================================
  VERIFICATION SUMMARY
====================================================================

Results: X/6 checks passed

✅ PASS  Collections
❌ FAIL  Appointments (legacy field names detected)
❌ FAIL  Availability (collection missing)
❌ FAIL  Services (collection missing)
⚠️   SOME CHECKS FAILED - RUN MIGRATION SCRIPT
```

### 3️⃣ **Run Migration Script** (5-10 minutes)

```powershell
# Run migration
python migrate_to_normalized_schema.py
```

**What it does:**
1. Converts appointments: `datetime` → `start/end`, `client_name` → `name`, `client_phone` → `phone`
2. Creates `availability` collection from business_config.opening_hours
3. Creates `services` collection from business_config.services
4. Creates `conversation_history` from existing conversations
5. Normalizes business_config field names

**Sample Output:**
```
============================================================
MIGRATING APPOINTMENTS
============================================================
Found 25 appointments to migrate
✓ Migrated appointment 507f...: John Doe - Haircut
✓ Migrated appointment 508a...: Jane Smith - Beard Trim
...

Appointments Migration Complete:
  - Migrated: 25
  - Errors: 0
  - Total: 25

✅ Migration completed successfully!

Do you want to remove non-essential collections? (yes/no):
```

**Type `yes`** to clean up old collections.

### 4️⃣ **Verify Migration** (2 minutes)

```powershell
# Run verification again
python verify_schema.py
```

**Expected Output:**
```
====================================================================
  VERIFICATION SUMMARY
====================================================================

Results: 6/6 checks passed

✅ PASS  Collections
✅ PASS  Appointments
✅ PASS  Availability
✅ PASS  Services
✅ PASS  Business Config
✅ PASS  Conversation History

====================================================================
  ✅ ALL CHECKS PASSED - SCHEMA IS NORMALIZED!
====================================================================
```

### 5️⃣ **Test Voice Agent** (5 minutes)

#### Option A: Dashboard Test Mode

1. Go to your dashboard: `http://localhost:5173`
2. Navigate to **Voice Agent** section
3. Click **"Test Agent"** or **"Start Test Call"**
4. Say: *"I want to book a haircut for tomorrow at 2 PM"*

**Expected:**
- ✅ Agent checks availability from MongoDB
- ✅ Creates appointment with `source: "voice"`
- ✅ Logs conversation to `conversation_history` with `type: "voice"`
- ✅ Returns confirmation

#### Option B: Check MongoDB Directly

```javascript
// In MongoDB Compass or shell:

// 1. Check if appointment was created with normalized schema
db.appointments.findOne({source: "voice"})
// Should show: name, phone, start, end (NOT client_name, datetime)

// 2. Check conversation history
db.conversation_history.find({type: "voice"}).limit(5)
// Should show voice messages

// 3. Check availability
db.availability.find({businessId: "default"})
// Should show 7 days (0-6)

// 4. Check services
db.services.find({businessId: "default"})
// Should show your services with durationMinutes, price
```

### 6️⃣ **Test WhatsApp Agent** (3 minutes)

Send a WhatsApp message:
```
"Book a haircut tomorrow at 3pm"
```

**Expected:**
- ✅ Creates appointment with `source: "text"`
- ✅ Logs to `conversation_history` with `type: "text"`
- ✅ Voice agent can see this appointment (shared DB)

### 7️⃣ **Verify Both Agents Share Data** (1 minute)

```python
# Run this in Python shell:
from database.mongo_config import get_database
import asyncio

async def check():
    db = get_database()
    
    # Count appointments by source
    voice_apts = await db.appointments.count_documents({"source": "voice"})
    text_apts = await db.appointments.count_documents({"source": "text"})
    
    print(f"Voice bookings: {voice_apts}")
    print(f"Text bookings: {text_apts}")
    print(f"Total: {voice_apts + text_apts}")
    
    # Count conversation history
    voice_msgs = await db.conversation_history.count_documents({"type": "voice"})
    text_msgs = await db.conversation_history.count_documents({"type": "text"})
    
    print(f"\nVoice messages: {voice_msgs}")
    print(f"Text messages: {text_msgs}")

asyncio.run(check())
```

---

## ✅ Success Checklist

After completing the above steps, you should have:

- [x] Backup of original database
- [x] All collections use normalized field names
- [x] `appointments` collection uses: `businessId`, `name`, `phone`, `start`, `end`, `source`
- [x] `availability` collection exists (7 entries per business)
- [x] `services` collection exists (your services)
- [x] `conversation_history` logs all interactions with `type` field
- [x] Voice agent can book appointments
- [x] WhatsApp agent still works
- [x] Both agents share the same MongoDB
- [x] Dashboard shows appointments from both sources

---

## 🎯 What You Achieved

### Before:
```
Voice Agent → ❓ Temporary Memory
WhatsApp Agent → ✅ MongoDB

Different schemas, no shared data
```

### After:
```
Voice Agent → ✅ MongoDB (normalized schema)
WhatsApp Agent → ✅ MongoDB (normalized schema)

Same collections, same logic, unified history
```

---

## 🆘 Troubleshooting

### Issue: Migration fails with "duplicate key error"

**Solution:**
```powershell
# Drop the problematic collection and retry
python
>>> from database.mongo_config import get_database
>>> import asyncio
>>> async def drop(): 
...     db = get_database()
...     await db.services.drop()
>>> asyncio.run(drop())
>>> exit()

# Then run migration again
python migrate_to_normalized_schema.py
```

### Issue: Voice agent returns "Database unavailable"

**Solution:**
```powershell
# Check MongoDB connection
python check_db.py

# If fails, check your .env file:
# MONGO_URI=mongodb://localhost:27017/ai_receptionist
```

### Issue: No availability slots returned

**Solution:**
```python
# Check if availability collection exists
from database.mongo_config import get_database
import asyncio

async def check():
    db = get_database()
    count = await db.availability.count_documents({})
    print(f"Availability entries: {count}")
    
    if count == 0:
        print("Run migration to create default availability")

asyncio.run(check())
```

---

## 📚 Next Steps

1. ✅ Complete migration
2. ✅ Test both voice and text agents
3. ✅ Monitor first real bookings
4. 📊 Set up analytics on `conversation_history.type`
5. 🎨 Customize voice agent prompts
6. 🔧 Fine-tune availability rules

---

## 📞 Need Help?

1. Check `backend/logs/` for error messages
2. Run `python verify_schema.py` to see current state
3. Review `VOICE_MONGODB_INTEGRATION.md` for detailed docs
4. Check MongoDB directly to verify data

---

**Total Time: ~20-30 minutes**

**Difficulty: Easy** (fully automated migration)

🎉 **You're done! Your voice agent is now fully integrated with MongoDB!**
