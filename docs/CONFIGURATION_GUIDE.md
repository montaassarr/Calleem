# Configuration Guide

## 📋 Overview

This guide covers all configuration options for the AI Receptionist system, from initial setup to advanced customization.

## 🔧 Environment Variables (.env)

The system uses environment variables for initial bootstrap. After first run, most settings migrate to the database.

### Required Variables

```bash
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist

# WhatsApp Cloud API
WHATSAPP_TOKEN=REDACTED
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token

# Groq API
GROQ_API_KEY=REDACTED
GROQ_MODEL=llama-3.3-70b-versatile

# JWT Security
SECRET_KEY=REDACTED
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Optional Variables

```bash
# Application
APP_NAME=AI Receptionist
DEBUG=true
ENVIRONMENT=development
API_V1_PREFIX=/api/v1

# Business Details (Bootstrap Only)
BUSINESS_NAME=Royal Fade Barbershop
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=info@barbershop.com
BUSINESS_ADDRESS=123 Main St, City, State
BUSINESS_HOURS=Monday-Saturday 9:00 AM - 8:00 PM
TIMEZONE=America/New_York
AVAILABLE_SERVICES=Haircut,Beard Trim,Fade,Hot Shave
DEFAULT_APPOINTMENT_DURATION=30

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Redis (Optional - for production caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Dashboard Access
MAX_DASHBOARD_USERS=5
ALLOW_SELF_REGISTRATION=false
```

## 🗄️ Database Configuration

### Business Configuration (Dynamic)

After first run, business settings move to `business_configs` collection:

```javascript
{
    "business_id": "default",  // For multi-tenancy
    "business_name": "Royal Fade Barbershop",
    "business_phone": "+1234567890",
    "business_email": "info@barbershop.com",
    "business_address": "123 Main St",
    "timezone": "America/New_York",
    
    "opening_hours": [
        {
            "day": "monday",
            "open": "09:00",
            "close": "20:00",
            "closed": false
        },
        {
            "day": "sunday",
            "open": "00:00",
            "close": "00:00",
            "closed": true
        }
    ],
    
    "services": [
        {
            "name": "Haircut",
            "description": "Professional haircut service",
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
        "voice_enabled": false,
        "voice_model": "whisper-large-v3"
    },
    
    "whatsapp_config": {
        "phone_number_id": "...",
        "access_token": "...",
        "verify_token": "...",
        "webhook_url": "https://your-domain.com/api/v1/webhook/sms"
    },
    
    "max_clients_per_day": 20,
    "default_appointment_duration": 30,
    
    "features_enabled": {
        "voice_agent": false,
        "email_notifications": false,
        "sms_reminders": false,
        "online_booking": true
    }
}
```

### Editing Configuration

#### Via API

```bash
# Get current config
curl -X GET http://localhost:8000/api/v1/business/config

# Update business details
curl -X PUT http://localhost:8000/api/v1/business/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "business_name": "Updated Name",
    "business_phone": "+1234567890"
  }'

# Update AI prompt
curl -X PUT http://localhost:8000/api/v1/business/config/ai-prompt \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "system_prompt": "You are Ava, the AI receptionist...",
    "temperature": 0.8
  }'

# Update WhatsApp config
curl -X PUT http://localhost:8000/api/v1/business/config/whatsapp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "access_token": "new_token_here",
    "phone_number_id": "123456789"
  }'

# Force reload config (clear cache)
curl -X POST http://localhost:8000/api/v1/business/config/reload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Via Dashboard UI

1. Login to admin dashboard
2. Navigate to **Settings**
3. Select configuration tab:
   - **Business Info**: Name, phone, email, address
   - **Operating Hours**: Set hours for each day
   - **Services**: Add/edit/remove services
   - **AI Configuration**: Edit system prompt, adjust temperature
   - **WhatsApp**: Update tokens and webhook URL

## 🤖 AI Configuration

### System Prompt

The system prompt defines the AI's personality and capabilities. It supports variable injection:

```
{business_name}      - Your business name
{business_phone}     - Contact phone number
{business_hours}     - Formatted operating hours
{services}           - List of services with duration
{current_datetime}   - Current date and time
{timezone}           - Business timezone
```

**Example**:

```
You are Ava, the friendly receptionist for {business_name}.

Current Date and Time: {current_datetime}

Your role is to help clients:
- Book appointments
- Answer questions about our services
- Provide business information

Our services: {services}
Operating hours: {business_hours}
Phone: {business_phone}

Always be warm, professional, and helpful.
```

### Model Selection

Available models (via Groq):

- `llama-3.3-70b-versatile` (Default - Best quality)
- `llama-3.1-8b-instant` (Faster, good quality)
- `mixtral-8x7b-32768` (Large context window)
- `gemma2-9b-it` (Lightweight)

### Temperature

Controls creativity/randomness:

- `0.0-0.3`: Very deterministic (factual responses)
- `0.4-0.7`: Balanced (Default: `0.7`)
- `0.8-1.0`: More creative/varied

### Max Tokens

Maximum response length:

- `200-300`: Very brief responses
- `500`: Default (good balance)
- `1000+`: Longer, detailed responses

## 📱 WhatsApp Configuration

### Getting WhatsApp Credentials

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a Business App
3. Add **WhatsApp** product
4. Get credentials:
   - **Phone Number ID**: Found in WhatsApp → API Setup
   - **Access Token**: Generate in WhatsApp → Configuration
   - **Verify Token**: Create your own (e.g., `my_verify_token_123`)

### Webhook Setup

1. In Meta for Developers:
   - Go to WhatsApp → Configuration
   - Click "Edit" on Webhook
   - Enter callback URL: `https://yourdomain.com/api/v1/webhook/sms`
   - Enter verify token (must match your `.env`)
   - Subscribe to `messages` webhook field

2. Update config in database:
```bash
curl -X PUT http://localhost:8000/api/v1/business/config/whatsapp \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "webhook_url": "https://yourdomain.com/api/v1/webhook/sms"
  }'
```

### Testing WhatsApp

```bash
# Test endpoint
curl -X POST http://localhost:8000/api/v1/webhook/test-whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Hello from AI Receptionist!"
  }'
```

## 🕐 Operating Hours Configuration

Configure hours for each day of the week:

```json
{
    "opening_hours": [
        {"day": "monday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "tuesday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "wednesday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "thursday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "friday", "open": "09:00", "close": "20:00", "closed": false},
        {"day": "saturday", "open": "10:00", "close": "18:00", "closed": false},
        {"day": "sunday", "open": "00:00", "close": "00:00", "closed": true}
    ]
}
```

**Notes**:
- Times in 24-hour format (`HH:MM`)
- Set `closed: true` for days off
- AI will automatically reject bookings outside hours

## 💈 Services Configuration

Add or modify services:

```json
{
    "services": [
        {
            "name": "Haircut",
            "description": "Professional haircut with style consultation",
            "duration_minutes": 30,
            "price": 25.00,
            "active": true
        },
        {
            "name": "Beard Trim",
            "description": "Precision beard trimming and shaping",
            "duration_minutes": 15,
            "price": 15.00,
            "active": true
        },
        {
            "name": "Hot Shave",
            "description": "Traditional hot towel shave",
            "duration_minutes": 20,
            "price": 30.00,
            "active": true
        }
    ]
}
```

## 🌍 Timezone Configuration

Set your business timezone for accurate appointment scheduling:

```json
{
    "timezone": "America/New_York"
}
```

**Common Timezones**:
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `Europe/London` - GMT/BST
- `Asia/Dubai` - Gulf Standard Time

[Full list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## 🔐 Authentication Configuration

### Creating Admin User

```bash
cd backend
python create_admin.py
```

Follow prompts to create admin account.

### JWT Settings

```bash
# .env
SECRET_KEY=REDACTED
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

**Generate secure secret key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Dashboard Access Control

```bash
MAX_DASHBOARD_USERS=5
ALLOW_SELF_REGISTRATION=false  # Set true to allow signups
```

## 🔧 Advanced Configuration

### Multi-Tenancy

Enable multi-tenant mode by using `X-Business-ID` header:

```bash
# Create config for tenant "salon_abc"
curl -X POST http://localhost:8000/api/v1/business/config \
  -H "X-Business-ID: salon_abc" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "ABC Salon",
    ...
  }'

# Get config for specific tenant
curl -X GET http://localhost:8000/api/v1/business/config \
  -H "X-Business-ID: salon_abc"
```

All API endpoints support `X-Business-ID` header. If not provided, defaults to `"default"`.

### Cache Configuration

Config cache TTL (in code):
```python
# backend/services/config_loader.py
self.cache_ttl_seconds = 300  # 5 minutes default
```

Force cache invalidation:
```bash
curl -X POST http://localhost:8000/api/v1/business/config/reload
```

### Feature Flags

```json
{
    "features_enabled": {
        "voice_agent": false,
        "email_notifications": false,
        "sms_reminders": false,
        "online_booking": true
    }
}
```

## 📊 Monitoring Configuration

### Logging

```bash
# .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2025-11-17T14:30:00",
    "database": "connected",
    "services": {
        "groq": "configured",
        "whatsapp": "configured",
        "mongodb": "connected"
    }
}
```

## 🚀 Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY` (32+ chars)
- [ ] Configure production `CORS_ORIGINS`
- [ ] Use MongoDB Atlas (not local)
- [ ] Enable HTTPS for webhook
- [ ] Set appropriate `LOG_LEVEL=WARNING`
- [ ] Configure rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Backup strategy for MongoDB
- [ ] Rotate WhatsApp tokens regularly

---

**Need Help?**
- Check logs: `backend/logs/app.log`
- API Docs: `http://localhost:8000/docs`
- GitHub Issues: [Report a bug](https://github.com/yourusername/ai-receptionist/issues)

**Last Updated**: November 17, 2025
