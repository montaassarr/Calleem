# AI Receptionist - Intelligent Barbershop Assistanttwilio code verification : 5ARRCD3J82L8WA445FU3YE17



![Python](https://img.shields.io/badge/python-3.10+-blue.svg)# 🤖 AI Receptionist for Barber Shop

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)

![React](https://img.shields.io/badge/React-18-blue.svg)[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()

![MongoDB](https://img.shields.io/badge/MongoDB-6.0-green.svg)[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)]()

![License](https://img.shields.io/badge/license-MIT-blue.svg)[![Frontend](https://img.shields.io/badge/frontend-React%2018-61dafb)]()

[![Database](https://img.shields.io/badge/database-MongoDB-47A248)]()

An intelligent AI-powered receptionist for barbershops that handles customer interactions via WhatsApp, manages appointments, and provides a comprehensive admin dashboard.[![AI](https://img.shields.io/badge/AI-Groq%20API-orange)]()



## 🌟 FeaturesAn intelligent, AI-powered virtual receptionist system for barber shops that handles customer communications via Twilio (SMS/Voice), manages appointments automatically, and provides a modern web dashboard for business management.



### 🤖 AI-Powered Conversations## 🎯 Project Overview

- Natural language understanding via Groq AI

- Intent classification (booking, cancellation, info requests)An intelligent, AI-powered virtual receptionist system for barber shops that handles customer communications via Twilio (SMS/Voice), manages appointments automatically, and provides a modern web dashboard for business management.

- Context-aware responses

- Multi-turn conversation handling### Key Features

- Automatic name extraction and validation

- 🤖 **AI-Powered Conversations**: Natural language understanding using Groq API

### 📱 WhatsApp Integration- 📱 **Twilio Integration**: Handle SMS and voice calls automatically

- WhatsApp Cloud API integration- 📅 **Smart Appointment Management**: Book, update, and cancel appointments via conversation

- Real-time message handling- 💬 **Conversation Transcripts**: Full history of all client interactions

- Automated appointment confirmations- 📊 **Admin Dashboard**: React-based dashboard for managing appointments and services

- Business hours awareness- ⚡ **Real-time Updates**: WebSocket support for instant dashboard updates

- Professional communication- 🔐 **Secure Authentication**: JWT-based user authentication



### 📅 Appointment Management### Technology Stack

- Create, update, and cancel appointments

- Real-time availability checking**Backend:**

- Automatic scheduling- FastAPI (Python 3.11+)

- SMS/WhatsApp notifications- MongoDB (Database)

- Conflict detection- Groq API (LLM)

- Twilio (SMS/Voice)

### 🎨 Modern Dashboard- WebSockets (Real-time)

- Responsive React + TypeScript frontend

- Real-time data updates (30s polling)**Frontend:**

- Beautiful UI with Shadcn components- React 18

- Appointment calendar view- Vite

- Conversation history- Tailwind CSS

- Service management- React Router DOM

- Analytics and insights- Axios

- Day.js

### 🔐 Security & Authentication

- JWT-based authentication## 📁 Project Structure

- Password hashing with Argon2

- Role-based access control```

- Secure API endpointsai_receptionist/

- CORS protection├── backend/                    # Python FastAPI backend

│   ├── main.py                # Application entry point

### 📊 Database│   ├── requirements.txt       # Python dependencies

- MongoDB for data persistence│   ├── .env.example          # Environment variables template

- Optimized queries with indexing│   ├── Dockerfile            # Docker configuration

- Conversation history storage│   │

- Appointment tracking│   ├── ai/                   # AI Logic Layer

- User management│   │   ├── groq_agent.py    # Groq API integration

│   │   ├── conversation_manager.py  # Conversation state

## 🚀 Quick Start│   │   ├── intents.py       # Intent classification

│   │   └── prompt_templates.py     # AI prompts

### Prerequisites│   │

│   ├── routers/             # API Routes

- Python 3.10+│   │   ├── webhook.py       # Twilio webhooks

- Node.js 18+│   │   ├── appointments.py  # Appointment CRUD

- MongoDB 6.0+│   │   ├── services.py      # Services management

- Git│   │   └── users.py         # Authentication

│   │

### Installation│   ├── models/              # Pydantic Models

│   │   ├── appointment.py

```bash│   │   ├── conversation.py

# Clone the repository│   │   ├── service.py

git clone https://github.com/montaassarr/ai-_receptionist.git│   │   └── user.py

cd ai-_receptionist│   │

│   ├── database/            # Database Layer

# Run automated setup│   │   └── mongo_config.py

chmod +x setup_complete.sh│   │

./setup_complete.sh│   └── utils/               # Utilities

```│       ├── config.py

│       ├── twilio_handler.py

### Configuration│       ├── text_formatter.py

│       └── datetime_utils.py

Edit `backend/.env`:│

├── frontend/                # React Frontend

```env│   ├── src/

# WhatsApp Cloud API│   │   ├── components/    # Reusable components

WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id│   │   │   ├── Navbar.jsx

WHATSAPP_ACCESS_TOKEN=REDACTED│   │   │   ├── Modal.jsx

WHATSAPP_VERIFY_TOKEN=your_verify_token│   │   │   ├── ProtectedRoute.jsx

│   │   │   └── LoadingSpinner.jsx

# Groq AI│   │   ├── pages/         # Page components

GROQ_API_KEY=REDACTED│   │   │   ├── Login.jsx

│   │   │   ├── Dashboard.jsx

# Security│   │   │   ├── Appointments.jsx

SECRET_KEY=REDACTED│   │   │   ├── Conversations.jsx

```│   │   │   └── Services.jsx

│   │   ├── lib/

### Running│   │   │   └── api.js     # Axios client

│   │   ├── App.jsx

```bash│   │   └── main.jsx

# Start both backend and frontend│   ├── package.json

./start.sh│   ├── vite.config.js

│   ├── tailwind.config.js

# Or start individually:│   └── .env.example

# Backend: cd backend && python main.py│

# Frontend: cd frontend && npm run dev├── docs/                    # Documentation

```│   ├── project_doc.md

│   ├── api_endpoints.md

Access:│   ├── database_schema.md

- **Frontend**: http://localhost:5173│   └── setup_guide.md

- **Backend API**: http://localhost:8000│

- **API Docs**: http://localhost:8000/docs├── stack_components.txt     # Complete stack documentation

├── docker-compose.yml       # Docker orchestration

## 📚 Documentation├── .gitignore

└── README.md               # This file

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions```

- **[API Documentation](docs/api_endpoints.md)** - API reference

- **[Database Schema](docs/database_schema.md)** - Database structure## 🚀 Quick Start

- **[Project Documentation](docs/project_doc.md)** - Architecture and design

- **[Testing Guide](COMPLETE_FIX_README.md)** - Testing and troubleshooting### One-Command Start (Recommended)



## 🏗️ Project Structure```bash

./start.sh

``````

ai-_receptionist/

├── backend/This will start:

│   ├── ai/                  # AI and conversation logic- MongoDB (if not running)

│   │   ├── conversation_manager.py- Backend API on port 8000

│   │   ├── groq_agent.py- Frontend Dashboard on port 5173

│   │   ├── intents.py

│   │   └── prompt_templates.pyThen open: **http://localhost:5173**

│   ├── database/            # Database configuration

│   │   └── mongo_config.pyLogin with: `admin` / `admin123`

│   ├── models/              # Data models

│   │   ├── appointment.py### Prerequisites

│   │   ├── conversation.py

│   │   ├── service.py- Python 3.11+

│   │   └── user.py- Node.js 18+

│   ├── routers/             # API routes- MongoDB (local or Atlas)

│   │   ├── appointments.py- Twilio Account (free tier)

│   │   ├── conversations.py- Groq API Key

│   │   ├── services.py

│   │   ├── users.py### 1. Clone and Setup Backend

│   │   └── webhook.py

│   ├── utils/               # Utilities```bash

│   │   ├── config.py# Navigate to project

│   │   ├── datetime_utils.pycd ai_receptionist/backend

│   │   ├── text_formatter.py

│   │   └── whatsapp_cloud.py# Create virtual environment

│   ├── main.py              # FastAPI applicationpython3 -m venv venv

│   ├── requirements.txt     # Python dependenciessource venv/bin/activate  # On Ubuntu/Linux

│   └── .env                 # Environment variables

├── frontend/# Install dependencies

│   ├── src/pip install -r requirements.txt

│   │   ├── api/             # API client

│   │   ├── components/      # React components# Copy environment template

│   │   ├── hooks/           # Custom hookscp .env.example .env

│   │   ├── lib/             # Utilities

│   │   ├── pages/           # Page components# Edit .env with your credentials

│   │   └── main.tsx         # App entry pointnano .env

│   ├── package.json         # Node dependencies```

│   └── vite.config.ts       # Vite configuration

├── docs/                    # Documentation### 2. Configure Environment Variables

├── logs/                    # Application logs

├── setup_complete.sh        # Automated setup scriptEdit `.env` file with your actual credentials:

├── start.sh                 # Start script

├── system_check.sh          # System verification```env

└── README.md                # This file# MongoDB

```MONGO_URI=mongodb://localhost:27017

MONGO_DB_NAME=ai_barber_receptionist

## 🛠️ Technology Stack

# Twilio

### BackendTWILIO_ACCOUNT_SID=your_account_sid

- **Framework**: FastAPITWILIO_AUTH_TOKEN=REDACTED

- **AI/ML**: Groq (Llama 3.3 70B)TWILIO_PHONE_NUMBER=+1234567890

- **Database**: MongoDB

- **Authentication**: JWT with Argon2# Groq

- **Async**: Motor (async MongoDB driver)GROQ_API_KEY=REDACTED

- **Messaging**: WhatsApp Cloud APIGROQ_MODEL=mixtral-8x7b-32768



### Frontend# JWT

- **Framework**: React 18 + TypeScriptSECRET_KEY=REDACTED

- **Build Tool**: Vite

- **UI Library**: Shadcn/ui + Radix UI# Business

- **Styling**: Tailwind CSSBUSINESS_NAME=Royal Fade Barbershop

- **State Management**: TanStack QueryBUSINESS_PHONE=+1234567890

- **HTTP Client**: Axios```



### DevOps### 3. Start MongoDB

- **Containerization**: Docker support

- **Monitoring**: Custom logging```bash

- **Testing**: Pytest, Jest# If using local MongoDB

- **CI/CD**: GitHub Actions readysudo systemctl start mongod



## 🧪 Testing# Or use MongoDB Atlas (cloud)

# Update MONGO_URI in .env with Atlas connection string

```bash```

# Run all tests

./run_tests.sh### 4. Run Backend



# System check```bash

./system_check.sh# Make sure you're in backend/ directory with venv activated

cd backend

# Test name extractionsource venv/bin/activate

./test_name_extraction.sh

# Create logs directory

# Check appointmentsmkdir -p logs

./check_appointment.sh

# Run with uvicorn

# Watch logsuvicorn main:app --reload --host 0.0.0.0 --port 8000

./watch_logs.sh```

```

Backend will be available at:

## 📊 Key Features Explained- API: http://localhost:8000

- Interactive Docs: http://localhost:8000/docs

### AI Conversation Flow- ReDoc: http://localhost:8000/redoc



1. User sends WhatsApp message### 5. Setup Frontend

2. System classifies intent (booking, info, etc.)

3. AI extracts entities (name, date, time, service)```bash

4. Context maintained across messages# Navigate to frontend directory

5. Appointment created when all info collectedcd ../frontend

6. Confirmation sent to user

# Install dependencies

### Name Extractionnpm install



Robust name extraction with:# Copy environment template

- Regex patterns for common phrasescp .env.example .env.local

- Whole-word validation (not substring matching)

- Invalid name filtering# Edit .env.local with backend URL

- Groq AI fallbacknano .env.local

- Multiple extraction attempts```



### Appointment CreationSet the API base URL in `.env.local`:

```env

- Validates all required fieldsVITE_API_BASE=http://localhost:8000/api/v1

- Checks business hours```

- Prevents double-booking

- Assigns unique IDs### 6. Run Frontend

- Sends confirmations

- Updates database atomically```bash

# Start development server

## 🔧 Configurationnpm run dev

```

### Environment Variables

Frontend will be available at:

| Variable | Description | Required |- Dashboard: http://localhost:5173

|----------|-------------|----------|- Login: http://localhost:5173/login

| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp Business Phone Number ID | Yes |

| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API Access Token | Yes |Default credentials:

| `WHATSAPP_VERIFY_TOKEN` | Webhook Verification Token | Yes |- Username: `admin`

| `GROQ_API_KEY` | Groq AI API Key | Yes |- Password: `admin123`

| `SECRET_KEY` | JWT Secret Key | Yes |

| `MONGODB_URL` | MongoDB Connection URL | No (default: localhost) |### 7. Setup Twilio Webhooks

| `DATABASE_NAME` | Database Name | No (default: ai_barber_receptionist) |

| `CORS_ORIGINS` | Allowed CORS Origins | No (default: localhost:5173) |1. Go to [Twilio Console](https://console.twilio.com/)

2. Navigate to Phone Numbers → Manage → Active Numbers

### Business Settings3. Select your phone number

4. Under "Messaging", set webhook URL to:

```env   ```

BUSINESS_NAME="Your Barber Shop"   https://your-domain.com/api/v1/webhook/sms

BUSINESS_PHONE=+1234567890   ```

BUSINESS_EMAIL=contact@yourbarbershop.com5. Under "Voice", set webhook URL to:

BUSINESS_ADDRESS="123 Main St, City, State 12345"   ```

```   https://your-domain.com/api/v1/webhook/voice

   ```

## 📈 Monitoring

**For local development**, use [ngrok](https://ngrok.com/):

### Health Check```bash

ngrok http 8000

```bash# Use the ngrok URL in Twilio webhooks

curl http://localhost:8000/health```

```

## 📖 API Documentation

### Logs

### Base URL

```bash```

# Backend logshttp://localhost:8000/api/v1

tail -f /tmp/backend.log```



# Filtered logs### Main Endpoints

./watch_logs.sh

```#### Appointments

- `POST /appointments/` - Create appointment

### Database Status- `GET /appointments/` - List appointments

- `GET /appointments/{id}` - Get appointment

```bash- `PUT /appointments/{id}` - Update appointment

mongosh ai_barber_receptionist --eval "- `DELETE /appointments/{id}` - Cancel appointment

  print('Conversations:', db.conversations.countDocuments());- `GET /appointments/stats/summary` - Get statistics

  print('Appointments:', db.appointments.countDocuments());

  print('Users:', db.users.countDocuments());#### Services

"- `POST /services/` - Create service

```- `GET /services/` - List services

- `GET /services/{id}` - Get service

## 🤝 Contributing- `PUT /services/{id}` - Update service

- `DELETE /services/{id}` - Deactivate service

Contributions are welcome! Please follow these steps:

#### Users & Auth

1. Fork the repository- `POST /users/register` - Register new user

2. Create a feature branch (`git checkout -b feature/amazing-feature`)- `POST /users/login` - Login (get JWT token)

3. Commit your changes (`git commit -m 'Add amazing feature'`)- `GET /users/me` - Get current user

4. Push to the branch (`git push origin feature/amazing-feature`)- `PUT /users/me` - Update current user

5. Open a Pull Request

#### Webhooks

## 🐛 Bug Reports- `POST /webhook/sms` - Twilio SMS webhook

- `POST /webhook/voice` - Twilio voice webhook

Please report bugs by opening an issue with:

- Clear descriptionSee `docs/api_endpoints.md` for detailed documentation.

- Steps to reproduce

- Expected vs actual behavior## 🧪 Testing

- System information

- Logs (if applicable)### Manual Testing



## 📝 LicenseTest the SMS flow:

1. Send a text to your Twilio number: "Hi, I want a haircut tomorrow at 3pm"

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.2. AI will respond and guide the booking process

3. Check appointments in the dashboard or via API

## 👥 Authors

### API Testing

- **Montassar** - *Initial work* - [@montaassarr](https://github.com/montaassarr)

Use the interactive docs at http://localhost:8000/docs

## 🙏 Acknowledgments

Or use curl:

- FastAPI for the excellent web framework```bash

- Groq for powerful AI capabilities# Get appointments

- Shadcn/ui for beautiful componentscurl http://localhost:8000/api/v1/appointments/

- MongoDB for flexible data storage

- Meta for WhatsApp Cloud API# Create appointment

curl -X POST http://localhost:8000/api/v1/appointments/ \

## 📞 Support  -H "Content-Type: application/json" \

  -d '{

For support:    "client_name": "John Doe",

- Check [INSTALLATION.md](INSTALLATION.md) for setup issues    "client_phone": "+1234567890",

- Review [COMPLETE_FIX_README.md](COMPLETE_FIX_README.md) for troubleshooting    "service": "Haircut",

- Open an issue on GitHub    "datetime": "2025-11-15T15:00:00",

- Check existing documentation in `/docs`    "duration_minutes": 30

  }'

## 🗺️ Roadmap```



- [ ] Multi-language support## 🔧 Configuration

- [ ] Voice message handling

- [ ] SMS integration### Business Settings

- [ ] Payment processing

- [ ] Advanced analyticsEdit `backend/.env` to customize:

- [ ] Mobile app

- [ ] Multi-tenant support```env

- [ ] Email notificationsBUSINESS_NAME=Your Barbershop Name

- [ ] Calendar integrations (Google, Outlook)BUSINESS_HOURS=Monday-Saturday 9:00 AM - 8:00 PM

- [ ] Customer loyalty programAVAILABLE_SERVICES=Haircut,Beard Trim,Fade,Hot Shave

DEFAULT_APPOINTMENT_DURATION=30

## ⚡ Performance```



- Handles 1000+ concurrent connections### AI Personality

- Sub-second response times

- Efficient MongoDB queriesCustomize the AI receptionist personality in:

- Optimized AI inference`backend/ai/prompt_templates.py`

- Real-time updates

## 📊 Database Schema

## 🔒 Security

MongoDB Collections:

- JWT authentication

- Argon2 password hashing1. **appointments** - Client appointments

- CORS protection2. **conversations** - Chat transcripts

- Input validation3. **services** - Available services

- SQL injection prevention (NoSQL)4. **users** - Admin users

- XSS protection

- Rate limiting readySee `docs/database_schema.md` for detailed schemas.

- Secure environment variables


## 🐳 Docker Deployment

### Quick Start with Docker

The easiest way to run the entire application:

```bash
# Start all services with Docker
./docker-start.sh
```

This will:
- Start MongoDB, Backend, and Frontend in Docker containers
- Wait for all services to be healthy
- Display service URLs and helpful information

Access the application at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Stop Services

```bash
./docker-stop.sh
```

### Manual Docker Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

📖 **For detailed Docker documentation, see [DOCKER.md](DOCKER.md)**

---

**Made with ❤️ for barbershops worldwide**

---

## Quick Links

- [Installation](INSTALLATION.md)
- [Docker Guide](DOCKER.md)
- [API Docs](http://localhost:8000/docs)
- [GitHub](https://github.com/montaassarr/ai-_receptionist)
- [Issues](https://github.com/montaassarr/ai-_receptionist/issues)

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

- [x] Backend API (FastAPI)
- [x] AI Conversation System (Groq)
- [x] Twilio Integration (SMS/Voice)
- [x] MongoDB Database
- [x] JWT Authentication
- [x] Frontend Dashboard (React + Vite + Tailwind)
- [x] Appointment Management UI
- [x] Conversation Viewer
- [x] Services Management
- [ ] Real-time WebSocket updates
- [ ] Voice call transcription
- [ ] Multi-language support
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Email notifications
- [ ] Automated appointment reminders
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
- [Groq API Docs](https://console.groq.com/docs)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)

---

**Built with ❤️ for barbershop owners who want to automate their booking process**
