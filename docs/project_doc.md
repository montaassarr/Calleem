# AI Receptionist Project - Step-by-Step Implementation Guide

## 📋 Project Overview

This document provides a comprehensive, phase-by-phase guide to implement the AI Receptionist system for barber shops. Follow each step sequentially to build the complete system.

---

## ✅ PHASE 1: Environment Setup & Core Infrastructure

### Step 1.1: System Requirements Installation

**Ubuntu/Linux Setup:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installations
python3 --version  # Should be 3.11+
node --version     # Should be 18+
mongosh --version  # Verify MongoDB
```

### Step 1.2: Project Structure Creation

```bash
cd /home/montassar/Desktop/ai_receptionist

# Backend structure already created
cd backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
```

### Step 1.3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your actual credentials
nano .env
```

**Required API Keys:**

1. **Twilio** (https://console.twilio.com/):
   - Sign up for free trial
   - Get Account SID
   - Get Auth Token
   - Get a phone number

2. **Groq API** (https://console.groq.com/):
   - Create account
   - Generate API key
   - Copy key to .env

3. **MongoDB** (if using Atlas):
   - Create cluster at https://cloud.mongodb.com/
   - Get connection string
   - Update MONGO_URI in .env

### Step 1.4: Database Initialization

```bash
# Start MongoDB (if not already running)
sudo systemctl start mongod

# Test MongoDB connection
mongosh

# In MongoDB shell:
use ai_barber_receptionist
db.createCollection("appointments")
db.createCollection("conversations")
db.createCollection("services")
db.createCollection("users")
exit
```

**Status:** ✅ Environment setup complete

---

## ✅ PHASE 2: Backend Core Implementation

### Step 2.1: Test FastAPI Server

```bash
# Ensure you're in backend/ with venv activated
cd backend
source venv/bin/activate

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:**
- Open browser: http://localhost:8000
- Should see: "AI Receptionist API is running!"
- Check docs: http://localhost:8000/docs

### Step 2.2: Create Initial Admin User

```bash
# Use the API docs or curl
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@barbershop.com",
    "username": "admin",
    "full_name": "Admin User",
    "password": "SecurePassword123!",
    "role": "admin"
  }'
```

### Step 2.3: Add Initial Services

```bash
# Add services via API
curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Haircut",
    "description": "Classic men haircut with styling",
    "duration_minutes": 30,
    "price": 25.00,
    "active": true
  }'

curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beard Trim",
    "description": "Professional beard trim and shape",
    "duration_minutes": 20,
    "price": 15.00,
    "active": true
  }'
```

**Status:** ✅ Backend core functional

---

## ✅ PHASE 3: Twilio Integration & Testing

### Step 3.1: Twilio Account Setup

1. Go to https://www.twilio.com/try-twilio
2. Sign up (free trial gives $15 credit)
3. Verify your phone number
4. Get a Twilio phone number
5. Copy Account SID and Auth Token to `.env`

### Step 3.2: Configure Ngrok for Local Testing

```bash
# Install ngrok (for local webhook testing)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at https://ngrok.com and get auth token
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Start ngrok tunnel
ngrok http 8000
```

**Copy the ngrok URL** (e.g., https://abcd1234.ngrok.io)

### Step 3.3: Configure Twilio Webhooks

1. Go to Twilio Console → Phone Numbers → Manage → Active Numbers
2. Click your phone number
3. Under "Messaging Configuration":
   - Webhook URL: `https://YOUR_NGROK_URL/api/v1/webhook/sms`
   - HTTP Method: POST
4. Under "Voice Configuration":
   - Webhook URL: `https://YOUR_NGROK_URL/api/v1/webhook/voice`
   - HTTP Method: POST
5. Save

### Step 3.4: Test SMS Flow

```bash
# Send a text to your Twilio number:
"Hi, I want to book a haircut"

# Check server logs for:
# - Incoming message
# - AI processing
# - Response sent

# Check conversation in database:
mongosh
use ai_barber_receptionist
db.conversations.find().pretty()
```

**Expected Flow:**
1. Client texts Twilio number
2. Twilio sends webhook to your server
3. AI processes message
4. AI responds naturally
5. Conversation saved to database

**Status:** ✅ Twilio integration working

---

## ✅ PHASE 4: AI Conversation Enhancement

### Step 4.1: Test AI Responses

Test different scenarios:

```
Scenario 1: Greeting
Input: "Hello"
Expected: Warm greeting, ask how to help

Scenario 2: Booking
Input: "I need a haircut tomorrow at 3pm"
Expected: Ask for name, confirm service

Scenario 3: Info Request
Input: "What services do you offer?"
Expected: List services

Scenario 4: Cancellation
Input: "Cancel my appointment"
Expected: Ask for details, confirm cancellation
```

### Step 4.2: Customize AI Prompts

Edit `backend/ai/prompt_templates.py` to customize:
- Business personality
- Response style
- Special greetings
- Business-specific information

### Step 4.3: Monitor Conversations

```bash
# View all conversations
curl http://localhost:8000/api/v1/appointments/

# Check conversation logs in MongoDB
mongosh
use ai_barber_receptionist
db.conversations.find().limit(10).sort({created_at:-1}).pretty()
```

**Status:** ✅ AI conversations optimized

---

## ✅ PHASE 5: Frontend Dashboard (Next Phase)

### Step 5.1: Initialize React App

```bash
# Navigate to project root
cd /home/montassar/Desktop/ai_receptionist

# Create frontend
npm create vite@latest frontend -- --template react
cd frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install axios react-router-dom framer-motion socket.io-client lucide-react date-fns react-hot-toast

# Initialize Tailwind
npx tailwindcss init -p
```

### Step 5.2: Configure Tailwind

Edit `frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Step 5.3: Create Dashboard Components

Components to create:
- Login page
- Dashboard overview
- Appointments list/calendar
- Conversation viewer
- Services manager

**Status:** 🚧 Frontend development in progress

---

## ✅ PHASE 6: Production Deployment

### Step 6.1: Docker Setup

```bash
# Build backend image
cd backend
docker build -t ai-receptionist-backend .

# Run with docker-compose
cd ..
docker-compose up -d
```

### Step 6.2: Deploy to Production

Options:
1. **Railway** (https://railway.app/)
2. **Render** (https://render.com/)
3. **DigitalOcean** (https://www.digitalocean.com/)
4. **AWS EC2**

### Step 6.3: Update Twilio Webhooks

Update Twilio webhooks with production URL:
```
https://your-production-domain.com/api/v1/webhook/sms
https://your-production-domain.com/api/v1/webhook/voice
```

**Status:** 🚧 Production deployment pending

---

## 📊 Progress Tracker

| Phase | Status | Completion |
|-------|--------|------------|
| 1. Environment Setup | ✅ Complete | 100% |
| 2. Backend Core | ✅ Complete | 100% |
| 3. Twilio Integration | ✅ Complete | 100% |
| 4. AI Enhancement | ✅ Complete | 100% |
| 5. Frontend Dashboard | 🚧 In Progress | 0% |
| 6. Production Deploy | 🚧 Pending | 0% |

---

## 🐛 Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod
```

**2. Twilio Webhook Not Working**
```bash
# Check ngrok is running
# Check firewall allows port 8000
# Verify webhook URL in Twilio console
# Check server logs
```

**3. Groq API Error**
```bash
# Verify API key in .env
# Check Groq API status
# Review error logs for details
```

**4. Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📝 Next Steps

1. **Complete Frontend**: Build React dashboard
2. **Add Features**: Calendar view, analytics
3. **Testing**: Write unit and integration tests
4. **Documentation**: API docs, user guide
5. **Deploy**: Production deployment
6. **Monitor**: Set up logging and monitoring

---

## 📚 Additional Resources

- See `api_endpoints.md` for API documentation
- See `database_schema.md` for data models
- See `setup_guide.md` for detailed setup
- See `stack_components.txt` for full tech stack

---

**Last Updated:** November 13, 2025
**Status:** Backend Complete, Frontend Pending
