# 🚀 Quick Start Guide - AI Receptionist v2.0

## ⚡ Get Up and Running in 10 Minutes

This guide gets you from zero to running AI Receptionist with the new enhanced brain.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10+ installed
- [ ] MongoDB running (local or Atlas)
- [ ] Groq API key (from https://console.groq.com)
- [ ] WhatsApp API credentials (optional for testing)
- [ ] Git installed

---

## 🏃 Quick Installation (Windows)

### Step 1: Clone and Setup (2 minutes)

```powershell
# Clone repository
git clone https://github.com/yourusername/ai-receptionist.git
cd ai-receptionist

# Run enhanced installation
.\install_enhanced.ps1
```

This script will:
- Create virtual environment
- Install all dependencies (including new AI frameworks)
- Verify installation

### Step 2: Configure Environment (2 minutes)

Create `.env` file in `backend/` directory:

```bash
# Minimum required configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist
GROQ_API_KEY=REDACTED
SECRET_KEY=REDACTED

# WhatsApp (optional for local testing)
WHATSAPP_TOKEN=REDACTED
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=my_verify_token_123
```

**Generate Secret Key**:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Create Admin User (1 minute)

```powershell
cd backend
python create_admin.py
```

Follow prompts:
- Username: `admin`
- Email: `admin@example.com`
- Password: (your choice)
- Full name: `Admin User`

### Step 4: Start Backend (1 minute)

```powershell
cd backend
..\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend Running**: http://localhost:8000

### Step 5: Test Installation (1 minute)

Open new terminal:

```powershell
# Test health
curl http://localhost:8000/health

# Test API docs
# Open browser: http://localhost:8000/docs

# Test business config
curl http://localhost:8000/api/v1/business/config
```

You should see business configuration with default settings!

---

## 🧪 Testing the AI Brain

### Test 1: Dynamic Prompt Generation

```powershell
# Start Python shell
cd backend
python

# Run test
from ai.brain import PromptBuilder
from services.config_loader import config_loader
from database.mongo_config import get_database
import asyncio

async def test_prompt():
    # This would need actual db connection
    config = {
        "business_name": "Test Barber",
        "services": [{"name": "Haircut", "duration_minutes": 30}],
        "business_hours": "Mon-Fri 9-5"
    }
    prompt = PromptBuilder.build_system_prompt(config)
    print(prompt)

asyncio.run(test_prompt())
```

### Test 2: Memory Engine

```python
from ai.brain import MemoryEngine
from ai.brain.memory_engine import ConversationMemory

# Create memory
memory = ConversationMemory("test_conv_123", "+1234567890")
memory.add_message("client", "I want to book a haircut")
memory.add_message("ai", "Great! What's your name?")

print(f"Messages: {len(memory.messages)}")
print(f"Conversation ID: {memory.conversation_id}")
```

### Test 3: Intent Classification

```python
from ai.brain import intent_classifier_engine
import asyncio

async def test_intent():
    result = await intent_classifier_engine.classify_intent(
        message="I want to book a haircut tomorrow at 3pm",
        context=None,
        groq_client=None  # Uses fallback mode
    )
    print(f"Intent: {result.intent}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")

asyncio.run(test_intent())
```

---

## 📱 WhatsApp Integration (Optional)

If you want to test WhatsApp messaging:

### Step 1: Setup ngrok (2 minutes)

```powershell
# Download ngrok from https://ngrok.com
# Then run:
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 2: Configure WhatsApp Webhook (3 minutes)

1. Go to https://developers.facebook.com
2. Your App → WhatsApp → Configuration
3. Edit Webhook:
   - Callback URL: `https://abc123.ngrok.io/api/v1/webhook/sms`
   - Verify Token: (from your `.env` file)
4. Subscribe to `messages` field
5. Click "Verify and Save"

### Step 3: Test WhatsApp Message

Send a message to your WhatsApp Business number:

```
Hi, I want to book a haircut
```

You should receive an AI response!

**Via API**:
```powershell
curl -X POST http://localhost:8000/api/v1/webhook/test-whatsapp `
  -H "Content-Type: application/json" `
  -d '{"to": "+1234567890", "message": "Test from API"}'
```

---

## 🎨 Frontend Setup (Optional - 5 minutes)

```powershell
# New terminal
cd frontend
npm install
npm run dev
```

Frontend will run at: http://localhost:5173

**Login**:
- Email: (from admin user creation)
- Password: (from admin user creation)

---

## 🔧 Configuration via API

### Get Current Config

```powershell
curl http://localhost:8000/api/v1/business/config
```

### Update Business Name

```powershell
# First, login to get token
$response = curl -X POST http://localhost:8000/api/v1/users/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=your_password"

# Extract token (manually from response)
$token = "your_jwt_token_here"

# Update config
curl -X PUT http://localhost:8000/api/v1/business/config `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{"business_name": "My Awesome Barbershop"}'
```

### Update AI Prompt

```powershell
curl -X PUT http://localhost:8000/api/v1/business/config/ai-prompt `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{
    "system_prompt": "You are Ava, the friendly AI receptionist for My Awesome Barbershop. You help clients book appointments, answer questions about our services, and provide business information. Always be warm, professional, and helpful.",
    "temperature": 0.7
  }'
```

---

## 🎯 Next Steps

### 1. Explore the AI Brain

Read the documentation:
- `docs/AI_BRAIN.md` - Detailed component guide
- `docs/ARCHITECTURE.md` - System architecture
- `docs/CONFIGURATION_GUIDE.md` - All configuration options

### 2. Customize Your Business

Via Dashboard or API:
- Update business info (name, phone, email, address)
- Set operating hours
- Add your services (with prices and durations)
- Customize AI prompt
- Configure WhatsApp

### 3. Test Conversation Flow

Send messages and watch:
- Conversation memory in action
- Intent classification
- Entity extraction
- Appointment booking validation

Check logs:
```powershell
cat backend/logs/app.log
```

### 4. Review API Documentation

Visit: http://localhost:8000/docs

Explore all endpoints:
- Business configuration
- Appointments
- Conversations
- Services
- Users
- Webhook

---

## 🚨 Common Issues

### MongoDB Not Running

**Symptom**: `Connection refused` error

**Fix**:
```powershell
# Start MongoDB
net start MongoDB

# Or manually
mongod --dbpath C:\data\db
```

### Port 8000 Already in Use

**Symptom**: `Address already in use`

**Fix**:
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

### Module Not Found

**Symptom**: `ModuleNotFoundError`

**Fix**:
```powershell
cd backend
pip install -r requirements.txt --upgrade
```

### Groq API Error

**Symptom**: `Unauthorized` or `Invalid API key`

**Fix**:
- Verify `GROQ_API_KEY` in `.env`
- Get new key from https://console.groq.com/keys
- Ensure no extra spaces or quotes in `.env`

---

## 📊 What You Now Have

✅ **Advanced AI Brain**
- Dynamic prompt generation
- Conversation memory with caching
- Appointment reasoning & validation
- Structured intent classification

✅ **Dynamic Configuration**
- MongoDB-based settings
- Hot reload capability
- Multi-tenant ready

✅ **Production-Ready Code**
- Proper error handling
- Logging
- API documentation
- Type safety (Pydantic)

✅ **Comprehensive Docs**
- Architecture guide
- AI Brain documentation
- Configuration reference

---

## 🎓 Learn More

- **Architecture**: `docs/ARCHITECTURE.md`
- **AI Brain**: `docs/AI_BRAIN.md`
- **Configuration**: `docs/CONFIGURATION_GUIDE.md`
- **Summary**: `REFACTORING_SUMMARY.md`

---

## ✅ Success Checklist

After following this guide, you should have:

- [x] Backend running on http://localhost:8000
- [x] MongoDB connected
- [x] Admin user created
- [x] Business config in database
- [x] AI Brain components working
- [x] API documentation accessible
- [x] Health check passing

**You're ready to build!** 🚀

---

**Quick Start Complete!**  
**Time Elapsed**: ~10 minutes  
**Version**: 2.0.0 Enhanced  
**Last Updated**: November 17, 2025
