# AI Receptionist - Architecture Documentation

## 🏗️ System Architecture

This document describes the enhanced architecture of the AI Receptionist system with advanced reasoning capabilities and multi-tenant support.

## 📊 High-Level Overview

```
┌─────────────────┐
│   WhatsApp API  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           AI Brain Reasoning Engine              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │   │
│  │  │ Prompt   │ │ Memory   │ │  Appointment    │  │   │
│  │  │ Builder  │ │ Engine   │ │  Reasoner       │  │   │
│  │  └──────────┘ └──────────┘ └─────────────────┘  │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │    Intent Classifier (Instructor)        │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Groq API   │ │  LangChain   │ │   CrewAI     │   │
│  │   (LiteLLM)  │ │   (Memory)   │ │ (Agents)     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                    MongoDB Database                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │Conversations │ │ Appointments │ │   Business   │   │
│  │   (Memory)   │ │              │ │    Config    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────┘
         ▲
         │
┌────────┴────────────────────────────────────────────────┐
│                React Frontend (Vite)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │  Dashboard   │ │  Settings    │ │ Appointments │   │
│  │  Analytics   │ │   Panel      │ │   Calendar   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🧠 AI Brain Components

### 1. Prompt Builder (`backend/ai/brain/prompt_builder.py`)

**Purpose**: Constructs dynamic AI system prompts from business configuration.

**Features**:
- Template variable injection (`{business_name}`, `{services}`, etc.)
- Cyranius-style barber shop prompt template
- Business hours formatting
- Service list generation

**Usage**:
```python
from ai.brain import PromptBuilder

system_prompt = PromptBuilder.build_system_prompt(
    config=business_config,
    current_time=datetime.now()
)
```

### 2. Memory Engine (`backend/ai/brain/memory_engine.py`)

**Purpose**: Manages conversation memory with MongoDB persistence.

**Features**:
- Short-term cache (in-memory, 1 hour TTL)
- Long-term persistence (MongoDB)
- User preference learning
- Conversation history retrieval

**Database Schema**:
```python
{
    "conversation_id": "conv_abc123",
    "phone_number": "+1234567890",
    "messages": [
        {"role": "client", "text": "...", "timestamp": "..."},
        {"role": "ai", "text": "...", "timestamp": "..."}
    ],
    "context": {"last_intent": "book_appointment"},
    "collected_info": {
        "client_name": "John",
        "service": "Haircut",
        "date": "tomorrow"
    },
    "created_at": "...",
    "updated_at": "..."
}
```

### 3. Appointment Reasoner (`backend/ai/brain/appointment_reasoning.py`)

**Purpose**: Advanced scheduling logic with conflict detection.

**Features**:
- Business hours validation
- Double-booking prevention
- Alternative slot suggestion
- Service validation
- Buffer time management (15 min default)

**Key Methods**:
```python
# Validate booking request
is_valid, message = await reasoner.validate_booking_request(
    db, config, booking_request
)

# Find available slots
slots = await reasoner.find_available_slots(
    db, config, date, duration_minutes=30
)

# Suggest alternatives
alternatives = await reasoner.suggest_alternatives(
    db, config, requested_datetime, days_ahead=7
)
```

### 4. Intent Classifier (`backend/ai/brain/intent_classifier.py`)

**Purpose**: Structured intent classification using Pydantic + Instructor.

**Supported Intents**:
- `greeting`
- `book_appointment`
- `update_appointment`
- `cancel_appointment`
- `check_availability`
- `service_info`
- `business_info`
- `general_question`
- `unknown`

**Output Structure**:
```python
{
    "intent": "book_appointment",
    "confidence": 0.95,
    "reasoning": "User explicitly mentioned scheduling a haircut"
}
```

## 💾 Database Schema

### Business Configuration Collection

```javascript
{
    "_id": ObjectId("..."),
    "business_id": "default",  // For multi-tenancy
    "business_name": "Royal Fade Barbershop",
    "business_phone": "+1234567890",
    "business_email": "info@barbershop.com",
    "timezone": "America/New_York",
    
    "opening_hours": [
        {"day": "monday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "sunday", "open": "00:00", "close": "00:00", "closed": true}
    ],
    
    "services": [
        {
            "name": "Haircut",
            "description": "Professional haircut",
            "duration_minutes": 30,
            "price": 25.00,
            "active": true
        }
    ],
    
    "ai_config": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 500,
        "system_prompt": "You are Ava...",
        "voice_enabled": false
    },
    
    "whatsapp_config": {
        "phone_number_id": "...",
        "access_token": "...",
        "verify_token": "...",
        "webhook_url": "..."
    },
    
    "max_clients_per_day": 20,
    "features_enabled": {
        "voice_agent": false,
        "email_notifications": false,
        "sms_reminders": false
    },
    
    "created_at": ISODate("..."),
    "updated_at": ISODate("...")
}
```

## 🔄 Request Flow

### WhatsApp Message Processing

1. **Webhook Receipt** → `/api/v1/webhook/sms` (POST)
2. **Extract Message** → Parse WhatsApp payload
3. **Load Configuration** → `config_loader.get_config(business_id)`
4. **Get/Create Memory** → `memory_engine.get_or_create_memory(phone_number)`
5. **Classify Intent** → `intent_classifier.classify_intent(message)`
6. **Extract Entities** → `intent_classifier.extract_entities(message)`
7. **Update Memory** → Store collected info in conversation memory
8. **Build Prompt** → `prompt_builder.build_system_prompt(config)`
9. **Generate Response** → Call Groq API with context
10. **Validate Booking** → If booking intent, run `appointment_reasoner`
11. **Create Appointment** → Insert into MongoDB if valid
12. **Save Memory** → Persist conversation state
13. **Send Response** → WhatsApp Cloud API

## 🔌 API Endpoints

### Business Configuration

- `GET /api/v1/business/config` - Get configuration
- `PUT /api/v1/business/config` - Update configuration
- `POST /api/v1/business/config/reload` - Force reload (clear cache)
- `GET /api/v1/business/config/ai-prompt` - Get AI prompt
- `PUT /api/v1/business/config/ai-prompt` - Update AI prompt
- `PUT /api/v1/business/config/whatsapp` - Update WhatsApp settings

### Multi-Tenancy

All endpoints support optional header:
```
X-Business-ID: tenant_abc123
```

If not provided, defaults to `"default"` (single-tenant mode).

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Web framework
- **Motor** - Async MongoDB driver
- **Pydantic v2** - Data validation
- **Groq** - Primary LLM provider
- **LangChain** - Memory & retrieval
- **CrewAI** - Multi-agent orchestration
- **LiteLLM** - Multi-model abstraction
- **Instructor** - Structured LLM outputs

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TanStack Query** - Data fetching
- **Shadcn/UI** - Component library
- **Tailwind CSS** - Styling

### Database
- **MongoDB** - Primary database
- Collections: `conversations`, `appointments`, `users`, `services`, `business_configs`

## 📦 Deployment Architecture

### Development
```
MongoDB (local) → FastAPI (localhost:8000) → React (localhost:5173)
                        ↓
                  Groq API (cloud)
                  WhatsApp Cloud API
```

### Production (Recommended)
```
MongoDB Atlas → FastAPI (Docker/Cloud Run) → React (Vercel/Netlify)
    ↑               ↓                            ↑
    |          Groq API                          |
    |          WhatsApp                          |
    └──────── Redis (optional) ──────────────────┘
```

## 🔐 Security

- JWT authentication for dashboard
- API key rotation support
- Sensitive config fields masked in responses
- Rate limiting on AI endpoints (recommended)
- CORS configured for production domains

## 📈 Scalability

### Horizontal Scaling
- Stateless FastAPI workers
- MongoDB replica sets
- Redis for shared caching

### Multi-Tenancy
- `business_id` field in all collections
- Per-tenant configuration isolation
- Middleware for tenant resolution

## 🧪 Testing Strategy

- **Unit Tests**: Individual AI components
- **Integration Tests**: Full conversation flows
- **Load Tests**: Concurrent WhatsApp messages
- **E2E Tests**: Frontend → Backend → MongoDB

## 📚 Key Files

- `backend/ai/brain/` - AI reasoning engine
- `backend/models/business_config.py` - Configuration schema
- `backend/services/config_loader.py` - Dynamic config management
- `backend/routers/business_config.py` - Configuration API
- `backend/main.py` - Application entry point

## 🔄 Migration Path

From static `.env` to dynamic database config:

1. System loads initial config from `settings.py`
2. First API call creates default business config in MongoDB
3. UI allows editing of business settings
4. All subsequent requests use database config
5. Cache layer (5 min TTL) reduces database load

## 🚀 Future Enhancements

- [ ] Voice agent integration (Whisper + TTS)
- [ ] Multi-language support
- [ ] Email notifications via SendGrid
- [ ] SMS reminders via Twilio
- [ ] Advanced analytics dashboard
- [ ] Client portal (self-service booking)
- [ ] Calendar sync (Google Calendar)
- [ ] Payment integration (Stripe)

---

**Last Updated**: November 17, 2025
**Version**: 2.0.0 (Enhanced AI Brain)
