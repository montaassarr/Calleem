# AI Receptionist for Barber Shop

## 🎯 Project Overview

An intelligent, AI-powered virtual receptionist system for barber shops that handles customer communications via Twilio (SMS/Voice), manages appointments automatically, and provides a modern web dashboard for business management.

### Key Features

- 🤖 **AI-Powered Conversations**: Natural language understanding using Groq API
- 📱 **Twilio Integration**: Handle SMS and voice calls automatically
- 📅 **Smart Appointment Management**: Book, update, and cancel appointments via conversation
- 💬 **Conversation Transcripts**: Full history of all client interactions
- 📊 **Admin Dashboard**: React-based dashboard for managing appointments and services
- ⚡ **Real-time Updates**: WebSocket support for instant dashboard updates
- 🔐 **Secure Authentication**: JWT-based user authentication

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- MongoDB (Database)
- Groq API (LLM)
- Twilio (SMS/Voice)
- WebSockets (Real-time)

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Framer Motion
- Axios

## 📁 Project Structure

```
ai_receptionist/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── Dockerfile            # Docker configuration
│   │
│   ├── ai/                   # AI Logic Layer
│   │   ├── groq_agent.py    # Groq API integration
│   │   ├── conversation_manager.py  # Conversation state
│   │   ├── intents.py       # Intent classification
│   │   └── prompt_templates.py     # AI prompts
│   │
│   ├── routers/             # API Routes
│   │   ├── webhook.py       # Twilio webhooks
│   │   ├── appointments.py  # Appointment CRUD
│   │   ├── services.py      # Services management
│   │   └── users.py         # Authentication
│   │
│   ├── models/              # Pydantic Models
│   │   ├── appointment.py
│   │   ├── conversation.py
│   │   ├── service.py
│   │   └── user.py
│   │
│   ├── database/            # Database Layer
│   │   └── mongo_config.py
│   │
│   └── utils/               # Utilities
│       ├── config.py
│       ├── twilio_handler.py
│       ├── text_formatter.py
│       └── datetime_utils.py
│
├── frontend/                # React Frontend (to be created)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── docs/                    # Documentation
│   ├── project_doc.md
│   ├── api_endpoints.md
│   ├── database_schema.md
│   └── setup_guide.md
│
├── stack_components.txt     # Complete stack documentation
├── docker-compose.yml       # Docker orchestration
├── .gitignore
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- Twilio Account (free tier)
- Groq API Key

### 1. Clone and Setup Backend

```bash
# Navigate to project
cd ai_receptionist/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Ubuntu/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your actual credentials:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=REDACTED
TWILIO_PHONE_NUMBER=+1234567890

# Groq
GROQ_API_KEY=REDACTED
GROQ_MODEL=mixtral-8x7b-32768

# JWT
SECRET_KEY=REDACTED

# Business
BUSINESS_NAME=Royal Fade Barbershop
BUSINESS_PHONE=+1234567890
```

### 3. Start MongoDB

```bash
# If using local MongoDB
sudo systemctl start mongod

# Or use MongoDB Atlas (cloud)
# Update MONGO_URI in .env with Atlas connection string
```

### 4. Run Backend

```bash
# Make sure you're in backend/ directory with venv activated
cd backend
source venv/bin/activate

# Create logs directory
mkdir -p logs

# Run with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Setup Twilio Webhooks

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to Phone Numbers → Manage → Active Numbers
3. Select your phone number
4. Under "Messaging", set webhook URL to:
   ```
   https://your-domain.com/api/v1/webhook/sms
   ```
5. Under "Voice", set webhook URL to:
   ```
   https://your-domain.com/api/v1/webhook/voice
   ```

**For local development**, use [ngrok](https://ngrok.com/):
```bash
ngrok http 8000
# Use the ngrok URL in Twilio webhooks
```

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Main Endpoints

#### Appointments
- `POST /appointments/` - Create appointment
- `GET /appointments/` - List appointments
- `GET /appointments/{id}` - Get appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Cancel appointment
- `GET /appointments/stats/summary` - Get statistics

#### Services
- `POST /services/` - Create service
- `GET /services/` - List services
- `GET /services/{id}` - Get service
- `PUT /services/{id}` - Update service
- `DELETE /services/{id}` - Deactivate service

#### Users & Auth
- `POST /users/register` - Register new user
- `POST /users/login` - Login (get JWT token)
- `GET /users/me` - Get current user
- `PUT /users/me` - Update current user

#### Webhooks
- `POST /webhook/sms` - Twilio SMS webhook
- `POST /webhook/voice` - Twilio voice webhook

See `docs/api_endpoints.md` for detailed documentation.

## 🧪 Testing

### Manual Testing

Test the SMS flow:
1. Send a text to your Twilio number: "Hi, I want a haircut tomorrow at 3pm"
2. AI will respond and guide the booking process
3. Check appointments in the dashboard or via API

### API Testing

Use the interactive docs at http://localhost:8000/docs

Or use curl:
```bash
# Get appointments
curl http://localhost:8000/api/v1/appointments/

# Create appointment
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

## 🔧 Configuration

### Business Settings

Edit `backend/.env` to customize:

```env
BUSINESS_NAME=Your Barbershop Name
BUSINESS_HOURS=Monday-Saturday 9:00 AM - 8:00 PM
AVAILABLE_SERVICES=Haircut,Beard Trim,Fade,Hot Shave
DEFAULT_APPOINTMENT_DURATION=30
```

### AI Personality

Customize the AI receptionist personality in:
`backend/ai/prompt_templates.py`

## 📊 Database Schema

MongoDB Collections:

1. **appointments** - Client appointments
2. **conversations** - Chat transcripts
3. **services** - Available services
4. **users** - Admin users

See `docs/database_schema.md` for detailed schemas.

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🛠️ Development

### Adding New Features

1. **New AI Intent**: Add to `backend/ai/intents.py`
2. **New API Route**: Create router in `backend/routers/`
3. **New Model**: Add Pydantic model in `backend/models/`

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Run tests
pytest backend/tests/
```

## 📝 Environment Variables Reference

See `backend/.env.example` for all available environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See `/docs` folder
- **Issues**: Open a GitHub issue
- **Stack Components**: See `stack_components.txt`

## 🎯 Roadmap

- [ ] Frontend React Dashboard
- [ ] Voice call transcription
- [ ] Multi-language support
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Email notifications
- [ ] Appointment reminders (automated)
- [ ] Analytics dashboard
- [ ] Mobile app

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
- [Groq API Docs](https://console.groq.com/docs)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)

---

**Built with ❤️ for barbershop owners who want to automate their booking process**
