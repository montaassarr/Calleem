# Setup Guide - AI Receptionist for Barber Shop

Complete step-by-step setup guide for Ubuntu/Linux systems.

---

## 📋 Prerequisites

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- 4GB RAM minimum (8GB recommended)
- 20GB free disk space
- Internet connection

### Required Accounts
1. **Twilio Account** - https://www.twilio.com/try-twilio (Free trial)
2. **Groq API Account** - https://console.groq.com/ (Free tier available)
3. **MongoDB Atlas** (Optional) - https://www.mongodb.com/cloud/atlas (Free tier)

---

## 🚀 Installation Steps

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python 3.11+

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify installation
python3.11 --version
```

### Step 3: Install MongoDB

```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update and install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod
mongosh --version
```

### Step 4: Install Node.js (for frontend)

```bash
# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### Step 5: Install Git

```bash
sudo apt install git -y
git --version
```

### Step 6: Clone or Navigate to Project

```bash
cd /home/montassar/Desktop/ai_receptionist
```

---

## ⚙️ Backend Setup

### Step 1: Create Virtual Environment

```bash
cd backend

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Python Dependencies

```bash
# Install all backend dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required Environment Variables:**

```env
# MongoDB (Local)
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist

# OR MongoDB Atlas (Cloud)
# MONGO_URI=mongodb+srv://REDACTED:REDACTED@cluster.mongodb.net/?retryWrites=true&w=majority

# Twilio (Get from https://console.twilio.com/)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=REDACTED
TWILIO_PHONE_NUMBER=+1234567890

# Groq API (Get from https://console.groq.com/)
GROQ_API_KEY=REDACTED
GROQ_MODEL=mixtral-8x7b-32768

# JWT Security
SECRET_KEY=REDACTED
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
APP_NAME=Royal Fade Barbershop AI Receptionist
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Business Details
BUSINESS_NAME=Royal Fade Barbershop
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=info@barbershop.com
BUSINESS_HOURS=Monday-Saturday 9:00 AM - 8:00 PM
TIMEZONE=America/New_York
AVAILABLE_SERVICES=Haircut,Beard Trim,Fade,Hot Shave,Hair & Beard Combo
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 4: Create Logs Directory

```bash
mkdir -p logs
```

### Step 5: Initialize Database

```bash
# Connect to MongoDB
mongosh

# Create database and collections
use ai_barber_receptionist
db.createCollection("appointments")
db.createCollection("conversations")
db.createCollection("services")
db.createCollection("users")

# Exit MongoDB shell
exit
```

### Step 6: Start Backend Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:**
- Open browser: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 📱 Twilio Setup

### Step 1: Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up (free trial gives $15 credit)
3. Verify your email and phone number

### Step 2: Get Phone Number

1. In Twilio Console, go to "Phone Numbers" → "Buy a Number"
2. Choose a number with SMS and Voice capabilities
3. Purchase the number (free with trial credit)

### Step 3: Get Credentials

1. From Twilio Console Dashboard:
   - Copy **Account SID**
   - Copy **Auth Token**
   - Copy your **Phone Number**
2. Update these in `backend/.env`

### Step 4: Setup Webhooks (Local Testing)

For local development, use ngrok:

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Sign up at https://ngrok.com and get auth token
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Start ngrok tunnel (in a new terminal)
ngrok http 8000
```

**Configure Twilio Webhooks:**

1. Go to Twilio Console → Phone Numbers → Active Numbers
2. Click your phone number
3. Under "Messaging":
   - Webhook URL: `https://YOUR_NGROK_URL/api/v1/webhook/sms`
   - HTTP Method: POST
4. Under "Voice":
   - Webhook URL: `https://YOUR_NGROK_URL/api/v1/webhook/voice`
   - HTTP Method: POST
5. Save

---

## 🔑 Groq API Setup

### Step 1: Create Account

1. Go to https://console.groq.com/
2. Sign up for free account
3. Verify email

### Step 2: Get API Key

1. Navigate to API Keys section
2. Click "Create API Key"
3. Copy the key (starts with `gsk_`)
4. Add to `backend/.env`:
   ```
   GROQ_API_KEY=REDACTED
   ```

---

## 🧪 Testing the System

### Test 1: API Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T...",
  "database": "connected",
  "services": {...}
}
```

### Test 2: Create Admin User

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@barbershop.com",
    "username": "admin",
    "full_name": "Admin User",
    "password": "Admin123!",
    "role": "admin"
  }'
```

### Test 3: Add Services

```bash
curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Haircut",
    "description": "Classic haircut",
    "duration_minutes": 30,
    "price": 25.00
  }'
```

### Test 4: SMS Flow

1. Send a text to your Twilio number:
   ```
   Hi, I want a haircut tomorrow at 3pm
   ```

2. Check server logs to see:
   - Incoming message received
   - AI processing
   - Response sent

3. Verify in MongoDB:
   ```bash
   mongosh
   use ai_barber_receptionist
   db.conversations.find().pretty()
   ```

---

## 🐳 Docker Setup (Optional)

### Install Docker

```bash
# Install Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker-compose --version
```

### Run with Docker Compose

```bash
# From project root
cd /home/montassar/Desktop/ai_receptionist

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## 🔍 Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check logs
sudo journalctl -u mongod -n 50
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Python Package Issues

```bash
# Reinstall all packages
pip install -r requirements.txt --force-reinstall

# Clear pip cache
pip cache purge
```

### Twilio Webhook Not Working

1. Check ngrok is running: `curl http://localhost:4040/status`
2. Verify webhook URL in Twilio console
3. Check server logs for incoming requests
4. Ensure backend server is running

---

## 📊 Monitoring

### View Server Logs

```bash
# Real-time logs
tail -f backend/logs/app.log

# Last 100 lines
tail -n 100 backend/logs/app.log
```

### Monitor System Resources

```bash
# CPU and Memory
htop

# MongoDB stats
mongosh
db.stats()
```

---

## 🚀 Production Deployment

### Prepare for Production

1. Update `.env`:
   ```env
   DEBUG=False
   ENVIRONMENT=production
   ```

2. Use strong SECRET_KEY:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. Update CORS_ORIGINS with your domain

### Deploy Options

- **Railway**: https://railway.app/
- **Render**: https://render.com/
- **DigitalOcean**: https://www.digitalocean.com/
- **AWS EC2**
- **Google Cloud Platform**

### SSL Certificate

Use Let's Encrypt for free SSL:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## 📝 Next Steps

1. ✅ Backend running and tested
2. ⬜ Create frontend React dashboard
3. ⬜ Add more AI features
4. ⬜ Deploy to production
5. ⬜ Configure domain and SSL
6. ⬜ Set up monitoring and alerts

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Twilio Docs**: https://www.twilio.com/docs
- **Groq API**: https://console.groq.com/docs
- **MongoDB**: https://docs.mongodb.com/

---

**Last Updated:** November 13, 2025

For issues or questions, check `docs/project_doc.md` or create an issue on GitHub.
