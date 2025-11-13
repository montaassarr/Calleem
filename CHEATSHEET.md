# AI Receptionist - Quick Reference Cheat Sheet

## 🚀 Quick Start Commands

### First Time Setup
```bash
cd /home/montassar/Desktop/ai_receptionist
./setup.sh
```

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start with Docker
```bash
docker-compose up -d
```

---

## 🔗 Important URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 Common API Calls

### Create Appointment
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_phone": "+1234567890",
    "service": "Haircut",
    "datetime": "2025-11-15T15:00:00",
    "duration_minutes": 30
  }'
```

### List Appointments
```bash
curl http://localhost:8000/api/v1/appointments/
```

### Register User
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

### Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -d "username=admin&password=Admin123!"
```

### Add Service
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

---

## 🗄️ MongoDB Commands

### Connect to MongoDB
```bash
mongosh
```

### Switch to Database
```javascript
use ai_barber_receptionist
```

### View Collections
```javascript
show collections
```

### Find Appointments
```javascript
db.appointments.find().pretty()
```

### Find Conversations
```javascript
db.conversations.find().sort({created_at:-1}).limit(10).pretty()
```

### Count Documents
```javascript
db.appointments.countDocuments()
db.conversations.countDocuments()
```

### Delete All (CAREFUL!)
```javascript
db.appointments.deleteMany({})
db.conversations.deleteMany({})
```

---

## 🐳 Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f backend
```

### Rebuild
```bash
docker-compose up -d --build
```

### Remove Volumes
```bash
docker-compose down -v
```

---

## 🔧 Troubleshooting

### MongoDB Not Starting
```bash
sudo systemctl status mongod
sudo systemctl restart mongod
sudo journalctl -u mongod -n 50
```

### Port Already in Use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Python Package Issues
```bash
pip install -r requirements.txt --force-reinstall
pip cache purge
```

### View Backend Logs
```bash
tail -f backend/logs/app.log
tail -n 100 backend/logs/app.log
grep -i error backend/logs/app.log
```

---

## 🌐 Ngrok (Local Twilio Testing)

### Start Ngrok
```bash
ngrok http 8000
```

### Get URL
Copy the https URL from ngrok output (e.g., https://abc123.ngrok.io)

### Update Twilio
Go to Twilio Console → Phone Numbers → Configure webhooks:
- SMS: `https://YOUR_NGROK_URL/api/v1/webhook/sms`
- Voice: `https://YOUR_NGROK_URL/api/v1/webhook/voice`

---

## 📁 Important Files

### Configuration
- `backend/.env` - Environment variables
- `backend/.env.example` - Environment template

### Documentation
- `README.md` - Project overview
- `PROJECT_SUMMARY.md` - Complete summary
- `stack_components.txt` - Tech stack details
- `docs/setup_guide.md` - Setup instructions
- `docs/api_endpoints.md` - API reference
- `docs/database_schema.md` - Database docs

### Code
- `backend/main.py` - FastAPI app entry
- `backend/routers/webhook.py` - Twilio webhooks
- `backend/ai/groq_agent.py` - AI integration
- `backend/ai/prompt_templates.py` - AI prompts

---

## 🔑 Environment Variables (Essential)

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Groq
GROQ_API_KEY=REDACTED
GROQ_MODEL=mixtral-8x7b-32768

# Security
SECRET_KEY=REDACTED
```

---

## 📊 Testing Flow

### 1. Start Backend
```bash
cd backend && source venv/bin/activate
uvicorn main:app --reload
```

### 2. Check Health
```bash
curl http://localhost:8000/health
```

### 3. Create Service
```bash
curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Haircut","duration_minutes":30,"price":25}'
```

### 4. Send Test SMS
Text your Twilio number: "Hi, I want a haircut"

### 5. Check Database
```bash
mongosh
use ai_barber_receptionist
db.conversations.find().pretty()
```

---

## 🎯 Quick File Navigation

```bash
# Main application
code backend/main.py

# AI configuration
code backend/ai/prompt_templates.py

# Environment variables
code backend/.env

# API docs
code docs/api_endpoints.md

# View logs
tail -f backend/logs/app.log
```

---

## 📚 Learning Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Twilio Quickstart**: https://www.twilio.com/docs/sms/quickstart/python
- **Groq Docs**: https://console.groq.com/docs
- **MongoDB Tutorial**: https://www.mongodb.com/docs/manual/tutorial/

---

## 🔍 Useful MongoDB Queries

```javascript
// Find today's appointments
db.appointments.find({
  datetime: {
    $gte: new Date(new Date().setHours(0,0,0)),
    $lt: new Date(new Date().setHours(23,59,59))
  }
})

// Find appointments by phone
db.appointments.find({client_phone: "+1234567890"})

// Find confirmed appointments
db.appointments.find({status: "confirmed"})

// Count by status
db.appointments.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}}
])

// Recent conversations
db.conversations.find().sort({created_at:-1}).limit(5)
```

---

## 🚨 Emergency Commands

### Kill All Python Processes
```bash
pkill -9 python
```

### Reset MongoDB
```bash
sudo systemctl stop mongod
sudo rm -rf /var/lib/mongodb/*
sudo systemctl start mongod
```

### Clean Docker
```bash
docker system prune -a --volumes
```

### Fresh Start
```bash
cd backend
deactivate  # if venv active
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Stack Info**: `stack_components.txt`
- **Summary**: `PROJECT_SUMMARY.md`
- **Setup**: `docs/setup_guide.md`

---

**Quick Tip**: Keep this file open while developing! 📌
