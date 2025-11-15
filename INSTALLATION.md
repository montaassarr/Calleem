# Installation Guide - AI Receptionist

Complete installation guide for setting up the AI Receptionist system from scratch.

## Table of Contents
- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   # Check version
   python3 --version
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # macOS
   brew install python@3.10
   
   # Windows
   # Download from https://www.python.org/downloads/
   ```

2. **Node.js 18 or higher**
   ```bash
   # Check version
   node --version
   
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # macOS
   brew install node
   
   # Windows
   # Download from https://nodejs.org/
   ```

3. **MongoDB 6.0 or higher**
   ```bash
   # Ubuntu/Debian
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   
   # macOS
   brew tap mongodb/brew
   brew install mongodb-community@6.0
   
   # Windows
   # Download from https://www.mongodb.com/try/download/community
   ```

4. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # macOS
   brew install git
   
   # Windows
   # Download from https://git-scm.com/download/win
   ```

### Optional (Recommended)

- **MongoDB Compass** - GUI for MongoDB
- **Postman** - API testing
- **VS Code** - Code editor

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **RAM**: 4GB
- **Storage**: 2GB free space
- **CPU**: 2 cores

### Recommended
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **CPU**: 4 cores
- **Internet**: Stable connection for API calls

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/montaassarr/ai-_receptionist.git
cd ai-_receptionist
```

### 2. Run Automated Setup

```bash
chmod +x setup_complete.sh
./setup_complete.sh
```

The setup script will:
- ✅ Check all prerequisites
- ✅ Create Python virtual environment
- ✅ Install backend dependencies
- ✅ Install frontend dependencies
- ✅ Setup database
- ✅ Create default services
- ✅ Generate environment configuration

### 3. Manual Setup (Alternative)

If automated setup fails, follow these steps:

#### Backend Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

#### Frontend Setup

```bash
cd frontend
npm install
cd ..
```

#### Database Setup

```bash
# Start MongoDB
sudo systemctl start mongod

# Initialize database
mongosh ai_barber_receptionist --eval "
db.createCollection('users');
db.createCollection('conversations');
db.createCollection('appointments');
db.createCollection('services');
"
```

---

## Configuration

### 1. Backend Configuration

Edit `backend/.env` and configure the following:

```env
# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=REDACTED
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Groq AI
GROQ_API_KEY=REDACTED

# Security (change in production!)
SECRET_KEY=REDACTED
ADMIN_PASSWORD=change_this_password

# Business Information
BUSINESS_NAME="Your Barber Shop"
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=contact@yourbarbershop.com
```

### 2. Get WhatsApp Cloud API Credentials

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use existing
3. Add WhatsApp product
4. Get your:
   - Phone Number ID
   - Access Token
   - Create a verify token (any random string)

**Detailed guide**: `docs/setup_guide.md`

### 3. Get Groq API Key

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create new API key
5. Copy and add to `.env`

### 4. Configure Webhook (for WhatsApp)

You'll need a public URL for webhooks. Options:

**Option A: ngrok (Development)**
```bash
# Install ngrok
snap install ngrok

# Start ngrok
ngrok http 8000

# Copy the HTTPS URL and configure in Meta Developer Console
```

**Option B: Production Domain**
```bash
# Use your domain with HTTPS
# Point webhook to: https://yourdomain.com/api/v1/webhook/sms
```

---

## Running the Application

### Development Mode

```bash
# Start everything with one command
./start.sh

# Or start individually:

# Terminal 1: Backend
source .venv/bin/activate
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Default Credentials

- **Username**: `admin`
- **Password**: `changeme123` (change this!)

---

## Verification

### Run System Check

```bash
./system_check.sh
```

Expected output:
```
✅ Backend is running
✅ MongoDB is connected
✅ Name extraction working
✅ Frontend is running
```

### Test Name Extraction

```bash
./test_name_extraction.sh
```

### Check Logs

```bash
# Watch backend logs
tail -f /tmp/backend.log

# Watch with filtering
./watch_logs.sh
```

---

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Enable auto-start
sudo systemctl enable mongod

# Check connection
mongosh --eval "db.adminCommand('ping')"
```

### Python Virtual Environment Issues

```bash
# Remove and recreate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend Port Already in Use

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
cd frontend
vite --port 3000
```

### Backend Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in backend/.env
PORT=8001
```

### Import Errors

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
cd backend
pip install --upgrade -r requirements.txt
```

### WhatsApp Webhook Not Receiving Messages

1. Check ngrok is running and URL is correct
2. Verify webhook configuration in Meta console
3. Check verify token matches
4. Look at backend logs for webhook activity
5. Test webhook manually:
   ```bash
   curl -X POST http://localhost:8000/api/v1/webhook/sms \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

### Name Extraction Not Working

```bash
# Test extraction
./test_name_extraction.sh

# Check logs
tail -f /tmp/backend.log | grep "extracted name"

# Manual test
python3 -c "
import sys
sys.path.insert(0, 'backend')
from utils.text_formatter import text_formatter
print(text_formatter.extract_name_from_text('My name is John'))
"
```

### Frontend Not Showing Appointments

1. Check backend API:
   ```bash
   curl http://localhost:8000/api/v1/appointments/
   ```

2. Check database:
   ```bash
   mongosh ai_barber_receptionist --eval "db.appointments.find().pretty()"
   ```

3. Check browser console for errors (F12)

4. Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R`)

---

## Database Management

### View Collections

```bash
mongosh ai_barber_receptionist
```

```javascript
// List all collections
show collections

// Count documents
db.appointments.countDocuments()
db.conversations.countDocuments()
db.users.countDocuments()

// View data
db.appointments.find().pretty()
db.conversations.find().pretty()
db.services.find().pretty()
```

### Clear Database

```bash
# Clear all appointments and conversations
mongosh ai_barber_receptionist --eval "
db.appointments.deleteMany({});
db.conversations.deleteMany({});
print('Database cleared');
"
```

### Backup Database

```bash
# Backup
mongodump --db ai_barber_receptionist --out backup/

# Restore
mongorestore --db ai_barber_receptionist backup/ai_barber_receptionist/
```

---

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Change `ADMIN_PASSWORD`
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS for all endpoints
- [ ] Configure proper CORS origins
- [ ] Set up SSL certificates
- [ ] Use environment-specific `.env` files
- [ ] Enable MongoDB authentication
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=<64-char-random-string>
CORS_ORIGINS=https://yourdomain.com
MONGODB_URL=mongodb://REDACTED:REDACTED@localhost:27017
```

### Using Gunicorn (Production Server)

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Build

```bash
cd frontend
npm run build

# Serve with nginx or other web server
# Build output is in: frontend/dist/
```

---

## Additional Resources

- **API Documentation**: `/docs/api_endpoints.md`
- **Database Schema**: `/docs/database_schema.md`
- **Project Documentation**: `/docs/project_doc.md`
- **Fix Documentation**: `/COMPLETE_FIX_README.md`
- **Name Extraction Fix**: `/NAME_EXTRACTION_FIX.md`

---

## Getting Help

1. Check logs: `tail -f /tmp/backend.log`
2. Run system check: `./system_check.sh`
3. Check documentation in `/docs`
4. Review error messages carefully
5. Test individual components separately

---

## Quick Reference

```bash
# Start application
./start.sh

# System check
./system_check.sh

# Watch logs
./watch_logs.sh

# Check appointments
./check_appointment.sh

# Test extraction
./test_name_extraction.sh

# Activate venv
source .venv/bin/activate

# Backend only
cd backend && python main.py

# Frontend only
cd frontend && npm run dev

# Run tests
./run_tests.sh
```

---

**Installation complete!** 🎉

For any issues, refer to the troubleshooting section or check the documentation.
