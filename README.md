# AI Voice + WhatsApp Receptionist SaaS Platform

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/montaassarr/ai-_receptionist)

> **The all-in-one AI-powered booking assistant for modern businesses**  
> Automate appointments via voice calls (Vapi) and WhatsApp messaging with intelligent conversation handling, multi-tenant support, and a powerful admin dashboard.

---

## 🌟 Overview

**AI Voice + WhatsApp Receptionist** is a production-ready SaaS platform that replaces traditional receptionists with AI agents capable of handling:

- **Voice calls** via Vapi (with ElevenLabs, OpenAI voices, or custom TTS)
- **WhatsApp messaging** through Meta's Cloud API
- **Appointment booking, rescheduling, cancellations** with real-time calendar sync
- **Multi-business tenancy** for agencies managing multiple clients
- **Admin dashboards** for monitoring conversations, logs, analytics, and settings

Perfect for barbershops, salons, spas, clinics, dental offices, restaurants, or any appointment-based business looking to automate customer interactions while maintaining a personalized touch.

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [DevOps & Tooling](#-devops--tooling-github-student-pack)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Roadmap](#-roadmap-6-month-plan)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

### 🎙️ AI Voice Receptionist

- **Inbound & outbound calls** via Vapi integration
- **Multi-voice support**: ElevenLabs (100+ voices), OpenAI (alloy, echo, fable, nova, onyx, shimmer), Azure, PlayHT, Deepgram
- **Real-time conversation** with context retention across turns
- **Tool execution**: check availability, book appointments, get services, reschedule, cancel
- **Call recording & transcription** (optional, configurable per business)
- **Custom prompts & greetings** editable per business tenant
- **Silence detection** and auto-hangup on goodbye
- **WebRTC browser sessions** for testing without phone numbers
- **Phone number provisioning** via Twilio integration

### 💬 WhatsApp AI Agent

- **Meta WhatsApp Cloud API** integration (verified business accounts)
- **Natural language understanding** via Groq (Llama 3.3 70B or Mixtral 8x7B)
- **Intent classification**: greeting, booking, rescheduling, cancellation, service inquiries, general info
- **Entity extraction**: names, dates, times, services
- **Multi-turn conversations** with state persistence
- **Automated confirmations** sent via WhatsApp
- **Business hours awareness** (prevents booking outside operating hours)
- **Smart name extraction** with fallback AI validation

### 📊 Admin Dashboard (React)

- **Appointment management**: CRUD operations with calendar view
- **Conversation history**: full transcripts with timestamps
- **Service management**: define offerings, pricing, duration
- **User management**: JWT-based authentication, role-based access
- **Business config**: customize prompts, voice settings, tools, hours
- **Real-time analytics**: call logs, booking trends, performance metrics
- **Voice settings page**: pick model (Groq/OpenAI), voice provider, tool toggles
- **Multi-tenant support**: manage multiple businesses from one dashboard

### 🛠️ Backend API (FastAPI)

- **RESTful endpoints** for appointments, services, users, conversations, voice config
- **Webhook receivers** for Vapi events (tool-calls, status-update, end-of-call-report) and WhatsApp messages
- **Asynchronous MongoDB** operations via Motor
- **Redis caching** for config, rate-limiting, session management
- **Background workers** (Celery) for async tasks (SMS, email, analytics)
- **Comprehensive logging** with Sentry error tracking
- **OpenAPI docs** at `/docs` and `/redoc`

### 🔧 Developer Tools

- **Docker Compose** for local development
- **GitHub Actions CI/CD** for automated testing & deployment
- **Pytest** for backend tests
- **Jest** for frontend tests
- **Environment validation** scripts
- **Database migration** utilities
- **Monitoring dashboards** (Datadog, Sentry)

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Phone Calls<br/>PSTN/VoIP]
        B[WhatsApp Messages<br/>Meta Cloud API]
        C[Admin Dashboard<br/>React SPA]
    end
    
    subgraph "Edge Layer"
        D[Nginx<br/>Reverse Proxy]
        E[Cloudflare<br/>CDN + DDoS]
    end
    
    subgraph "Application Layer"
        F[FastAPI Backend<br/>Python 3.11]
        G[Vapi Voice Agent<br/>WebRTC/SIP]
        H[Redis<br/>Cache + Queue]
        I[Celery Workers<br/>Async Tasks]
    end
    
    subgraph "Data Layer"
        J[(MongoDB Atlas<br/>Primary DB)]
        K[(MongoDB Local<br/>Dev/Test)]
        L[S3 Compatible<br/>Call Recordings]
    end
    
    subgraph "External Services"
        M[Groq API<br/>LLM Inference]
        N[ElevenLabs<br/>Voice Synthesis]
        O[Twilio<br/>Phone Numbers]
        P[Meta Graph API<br/>WhatsApp]
        Q[Sentry<br/>Error Tracking]
        R[Datadog<br/>APM + Logs]
    end
    
    A -->|SIP/WebRTC| G
    G -->|Webhook| D
    B -->|HTTPS| D
    C -->|HTTPS| E
    
    D --> F
    E --> F
    
    F --> H
    F --> J
    F --> M
    F --> P
    
    G --> N
    G --> O
    
    F --> I
    I --> J
    I --> H
    
    F --> Q
    F --> R
    
    H -.Pub/Sub.-> I
    I -.Store.-> L
```

### Architecture Layers Explained

#### 1. **Client Layer**
- **Phone Calls**: PSTN or VoIP calls routed to Vapi's infrastructure
- **WhatsApp**: Messages sent via Meta's Cloud API webhook
- **Dashboard**: React SPA served via Nginx with Cloudflare caching

#### 2. **Edge Layer**
- **Nginx**: Reverse proxy, SSL termination, load balancing, static file serving
- **Cloudflare**: Free CDN, DDoS protection, DNS, SSL certificates

#### 3. **Application Layer**
- **FastAPI Backend**: Main orchestrator handling webhooks, API requests, business logic
- **Vapi Agent**: Manages voice sessions, executes tools, streams audio
- **Redis**: Caches config, manages rate limits, queues background tasks
- **Celery Workers**: Process async jobs (send SMS, generate reports, sync data)

#### 4. **Data Layer**
- **MongoDB Atlas**: Production database (replicated, auto-backup, monitoring)
- **MongoDB Local**: Development & testing instance
- **S3 Compatible Storage**: (LocalStack for dev, AWS/DigitalOcean Spaces for prod) stores call recordings

#### 5. **External Services**
- **Groq**: Powers conversational AI with Llama 3.3 70B or Mixtral 8x7B
- **ElevenLabs**: Text-to-speech for voice agent
- **Twilio**: Phone number provisioning, SMS fallback
- **Meta Graph API**: WhatsApp messaging infrastructure
- **Sentry**: Real-time error tracking and crash reporting
- **Datadog**: Application performance monitoring, log aggregation, alerting

---

## 🔧 Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.109+ | High-performance async web framework |
| **Language** | Python 3.11+ | Core backend logic |
| **Database** | MongoDB 6.0+ | NoSQL document store for appointments, conversations, users |
| **Cache** | Redis 7.0+ | Session management, rate-limiting, task queue |
| **Task Queue** | Celery | Background jobs (SMS, email, analytics) |
| **AI/LLM** | Groq API | Llama 3.3 70B, Mixtral 8x7B for conversation |
| **Voice** | Vapi + ElevenLabs | Voice agent infrastructure + TTS |
| **Messaging** | Meta WhatsApp Cloud API | WhatsApp integration |
| **Auth** | JWT + Argon2 | Token-based authentication with secure hashing |
| **ORM** | Motor (async) | Async MongoDB driver |
| **Validation** | Pydantic v2 | Data validation and serialization |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React 18.3 | Component-based UI library |
| **Build Tool** | Vite 5.x | Fast development server & bundler |
| **Language** | TypeScript | Type-safe JavaScript |
| **UI Library** | Shadcn/ui + Radix UI | Accessible component primitives |
| **Styling** | Tailwind CSS 3.x | Utility-first CSS framework |
| **State** | TanStack Query (React Query) | Server state management |
| **HTTP Client** | Axios | API communication |
| **Routing** | React Router v6 | Client-side routing |
| **Forms** | React Hook Form | Form validation & submission |
| **Charts** | Recharts | Analytics visualizations |
| **Date** | Day.js | Lightweight date manipulation |

### DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker + Docker Compose | Local dev environment & deployment |
| **CI/CD** | GitHub Actions | Automated testing, builds, deployments |
| **Hosting** | DigitalOcean Droplets | Production VM hosting |
| **Database Hosting** | MongoDB Atlas | Managed MongoDB cluster |
| **Monitoring** | Datadog | APM, logs, metrics, alerts |
| **Error Tracking** | Sentry | Real-time crash reporting |
| **Secrets** | 1Password / Doppler | Environment variable management |
| **CDN** | Cloudflare | Edge caching, DDoS protection |
| **DNS** | Namecheap + Cloudflare | Domain management |
| **SSL** | Let's Encrypt (via Nginx) | Free SSL certificates |
| **Load Balancing** | Nginx | Reverse proxy, SSL termination |
| **Analytics** | SimpleAnalytics / Posthog | Privacy-focused user analytics |

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **MongoDB 6.0+** (local or [Atlas account](https://www.mongodb.com/cloud/atlas))
- **Redis 7.0+** (local or cloud instance)
- **Git** ([Download](https://git-scm.com/))

**Optional but recommended:**
- Docker & Docker Compose
- ngrok (for local webhook testing)

### Quick Start (5 minutes)

#### 1. Clone the Repository

```bash
git clone https://github.com/montaassarr/ai-_receptionist.git
cd ai-_receptionist
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials (see Configuration section below)
# nano .env  # or use your preferred editor
```

#### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local
# nano .env.local
```

Set in `.env.local`:
```env
VITE_API_BASE=http://localhost:8000/api/v1
```

#### 4. Start Services

**Option A: Docker Compose (Recommended)**

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Option B: Manual Start**

```bash
# Terminal 1 - MongoDB (if not using Atlas)
mongod --dbpath ./data/db

# Terminal 2 - Redis
redis-server

# Terminal 3 - Backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4 - Frontend
cd frontend
npm run dev
```

#### 5. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

**⚠️ Change these credentials immediately in production!**

#### 6. Test the CRUD Demo

Verify database integration:

```bash
cd backend
python scripts/voice_crud_demo.py
```

This will:
- Create a demo business config
- Read voice settings from MongoDB
- Update prompt, voice, and tool settings
- Delete the demo config
- Display the shared tool catalog

---

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env` from the template and configure:

```env
# ============================================================================
# DATABASE
# ============================================================================
MONGO_URI=mongodb://localhost:27017
# For MongoDB Atlas:
# MONGO_URI=mongodb+srv://REDACTED:REDACTED@cluster.mongodb.net/?retryWrites=true&w=majority

MONGO_DB_NAME=ai_barber_receptionist

# ============================================================================
# REDIS
# ============================================================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# For Redis Cloud:
# REDIS_HOST=redis-12345.c1.us-east-1.redislabs.com
# REDIS_PORT=12345
# REDIS_PASSWORD=your_redis_password

# ============================================================================
# WHATSAPP CLOUD API
# ============================================================================
# Get from: https://developers.facebook.com/apps/
WHATSAPP_TOKEN=REDACTED
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token

# ============================================================================
# VAPI VOICE AGENT
# ============================================================================
# Get from: https://dashboard.vapi.ai/
VAPI_API_KEY=REDACTED
VAPI_PUBLIC_KEY=REDACTED
VAPI_WEBHOOK_URL=https://your-domain.com/api/v1/voice/webhook
VAPI_SERVER_SECRET=your_webhook_secret

# Optional: Pre-created assistant ID (otherwise auto-created)
VAPI_ASSISTANT_ID=

# WebRTC settings for browser testing
VOICE_AGENT_WEBRTC_PUBLIC_KEY=your_vapi_public_key
VOICE_AGENT_WEBRTC_ASSISTANT_ID=
VOICE_AGENT_WEBRTC_SESSION_TTL_MINUTES=10

# ============================================================================
# GROQ API (LLM)
# ============================================================================
# Get from: https://console.groq.com/
GROQ_API_KEY=REDACTED
GROQ_MODEL=llama-3.3-70b-versatile
# Alternatives: llama-3.1-70b-versatile, mixtral-8x7b-32768

# ============================================================================
# ELEVENLABS (OPTIONAL VOICE)
# ============================================================================
# Get from: https://elevenlabs.io/
ELEVENLABS_API_KEY=REDACTED
ELEVENLABS_DEFAULT_VOICE=rachel

# ============================================================================
# JWT & SECURITY
# ============================================================================
SECRET_KEY=REDACTED
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ============================================================================
# BUSINESS DETAILS
# ============================================================================
BUSINESS_NAME=Royal Fade Barbershop
BUSINESS_PHONE=+15556441379
BUSINESS_EMAIL=info@royalfade.com
BUSINESS_ADDRESS=123 Main Street, City, State 12345
BUSINESS_HOURS=Monday-Saturday 9:00 AM - 8:00 PM, Sunday Closed
TIMEZONE=America/New_York

# Services (comma-separated)
AVAILABLE_SERVICES=Haircut,Beard Trim,Fade,Hot Shave,Hair & Beard Combo
DEFAULT_APPOINTMENT_DURATION=30

# ============================================================================
# CORS
# ============================================================================
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://yourdomain.com"]

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ============================================================================
# CELERY (BACKGROUND TASKS)
# ============================================================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ============================================================================
# MONITORING
# ============================================================================
# Sentry DSN (optional)
SENTRY_DSN=

# Datadog API Key (optional)
DATADOG_API_KEY=

# ============================================================================
# ENVIRONMENT
# ============================================================================
APP_NAME=AI Voice + WhatsApp Receptionist
DEBUG=True
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```env
# Backend API base URL
VITE_API_BASE=http://localhost:8000/api/v1

# For production:
# VITE_API_BASE=https://api.yourdomain.com/api/v1

# Analytics (optional)
VITE_ANALYTICS_ID=

# Sentry DSN (optional)
VITE_SENTRY_DSN=
```

### Webhook Setup for Local Development

Use [ngrok](https://ngrok.com/) to expose your local server:

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update .env:
VAPI_WEBHOOK_URL=https://abc123.ngrok.io/api/v1/voice/webhook

# For WhatsApp, configure webhook in Meta Developer Console:
# https://abc123.ngrok.io/api/v1/webhook
```

---

## 🎓 DevOps & Tooling (GitHub Student Pack)

This SaaS leverages **free credits and tools from the [GitHub Student Developer Pack](https://education.github.com/pack)** to minimize costs while building production-grade infrastructure.

### 🟦 DigitalOcean ($200 Free Credit)

**Use Case:** Host backend, frontend, databases, Redis

**Setup:**
1. Sign up at [DigitalOcean Education](https://www.digitalocean.com/github-students)
2. Redeem $200 credit (valid 1 year)
3. Create Droplets:
   - **Backend Droplet** (4GB RAM, 2 vCPUs) - $24/month
   - **Frontend Droplet** (1GB RAM, 1 vCPU) - $6/month
   - **Database Droplet** (2GB RAM, 1 vCPU) - $12/month (or use Managed MongoDB)
4. Optional: Use **DigitalOcean Spaces** for call recording storage ($5/month, 250GB)

**Deployment:**
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone https://github.com/montaassarr/ai-_receptionist.git
cd ai-_receptionist

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

---

### 🟧 MongoDB Atlas ($50 Free Credit)

**Use Case:** Production database with auto-backups, monitoring, alerts

**Setup:**
1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create M0 cluster (free tier, 512MB storage)
3. Whitelist IP addresses or use 0.0.0.0/0 for development
4. Create database user
5. Get connection string:
   ```
   mongodb+srv://REDACTED:REDACTED@cluster0.xxxxx.mongodb.net/ai_barber_receptionist?retryWrites=true&w=majority
   ```
6. Update `MONGO_URI` in `.env`

**Features:**
- Automated backups
- Point-in-time recovery
- Monitoring dashboard
- Alerts (disk usage, connection spikes)
- Multi-region replication

---

### 🟩 Sentry (Error Tracking)

**Use Case:** Real-time crash reporting, performance monitoring

**Setup:**
1. Sign up at [Sentry.io](https://sentry.io/for/students/)
2. Create projects for backend (Python) and frontend (React)
3. Get DSN keys
4. Configure `.env`:
   ```env
   SENTRY_DSN=https://xxxxx@yyyyy.ingest.sentry.io/zzzzz
   ```
5. Install SDKs:
   ```bash
   # Backend
   pip install sentry-sdk[fastapi]
   
   # Frontend
   npm install @sentry/react
   ```

**Backend Integration (`backend/main.py`):**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
)
```

**Frontend Integration (`frontend/src/main.tsx`):**
```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
});
```

---

### 🟪 Datadog (Monitoring & APM)

**Use Case:** Server metrics, logs, traces, alerts

**Setup:**
1. Sign up at [Datadog Education](https://www.datadoghq.com/partner/github-students/)
2. Install agent on DigitalOcean droplet:
   ```bash
   DD_API_KEY=your_datadog_api_key DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
   ```
3. Configure APM for Python:
   ```bash
   pip install ddtrace
   
   # Run with tracing
   ddtrace-run uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. View dashboards: https://app.datadoghq.com

**Monitors:**
- CPU > 80% for 5 minutes → alert
- Memory > 90% → alert
- API latency > 2s → alert
- Error rate > 5% → alert

---

### 🟥 GitHub Actions (CI/CD)

**Use Case:** Automated testing, building, deployment

**Workflow (`.github/workflows/deploy.yml`):**
```yaml
name: Deploy to Production

on:
  push:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/
      
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose -f docker-compose.prod.yml build
      
      - name: Deploy to DigitalOcean
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DO_HOST }}
          username: root
          key: ${{ secrets.DO_SSH_KEY }}
          script: |
            cd /opt/ai-receptionist
            git pull origin master
            docker-compose -f docker-compose.prod.yml up -d --build
```

**Secrets to Add:**
- `DO_HOST`: DigitalOcean droplet IP
- `DO_SSH_KEY`: Private SSH key
- `MONGO_URI`: Production MongoDB connection string
- `SENTRY_DSN`: Sentry DSN
- `VAPI_API_KEY`: Vapi API key

---

### 🟦 BrowserStack / LambdaTest

**Use Case:** Cross-browser testing for dashboard

**Setup:**
1. Sign up at [BrowserStack for Students](https://www.browserstack.com/github-students)
2. Run tests against real browsers:
   ```bash
   npm install --save-dev @browserstack/cypress-browserstack
   
   # cypress.config.js
   module.exports = {
     projectId: 'your-project-id',
     env: {
       username: process.env.BROWSERSTACK_USERNAME,
       accessKey: process.env.BROWSERSTACK_ACCESS_KEY,
     },
   };
   ```

---

### 🟨 Namecheap (Free Domain)

**Use Case:** Custom domain for production

**Setup:**
1. Claim free domain at [Namecheap Education](https://nc.me/)
2. Point DNS to Cloudflare:
   - Nameservers: `ns1.cloudflare.com`, `ns2.cloudflare.com`
3. Add A records in Cloudflare:
   - `@` → DigitalOcean droplet IP
   - `api` → DigitalOcean droplet IP

---

### 🟣 1Password / Doppler (Secrets Management)

**Use Case:** Secure .env file management

**Doppler Setup:**
```bash
# Install CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login
doppler login

# Setup project
doppler setup

# Add secrets
doppler secrets set MONGO_URI VAPI_API_KEY GROQ_API_KEY ...

# Run app with secrets
doppler run -- uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### 🟩 Stripe (Payment Processing)

**Use Case:** Subscription billing for SaaS clients

**Setup:**
1. Sign up at [Stripe](https://stripe.com/)
2. First $1000 in fees waived for students
3. Install SDK:
   ```bash
   pip install stripe
   ```
4. Create subscription tiers:
   - **Starter**: $29/month (1 business, 100 calls/month)
   - **Pro**: $99/month (5 businesses, 1000 calls/month)
   - **Enterprise**: $299/month (unlimited)

**Backend Integration:**
```python
import stripe
stripe.api_key = settings.STRIPE_API_KEY

@router.post("/create-subscription")
async def create_subscription(customer_email: str, plan: str):
    customer = stripe.Customer.create(email=customer_email)
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": PLAN_PRICE_IDS[plan]}],
    )
    return {"subscription_id": subscription.id}
```

---

### 🟦 LocalStack (AWS Emulator)

**Use Case:** Develop with S3, Lambda, SNS locally before going to AWS

**Setup:**
```bash
# Install
pip install localstack

# Start
localstack start

# Configure AWS CLI to use LocalStack
aws configure --profile localstack
# Endpoint: http://localhost:4566

# Create S3 bucket for call recordings
aws --endpoint-url=http://localhost:4566 s3 mb s3://call-recordings

# Upload file
aws --endpoint-url=http://localhost:4566 s3 cp recording.mp3 s3://call-recordings/
```

---

### 🎯 Additional Best-Practice Tools

| Tool | Use Case | Cost |
|------|----------|------|
| **Posthog** | Privacy-focused analytics | Free tier: 1M events/month |
| **Vercel** | Frontend preview deployments | Free for personal projects |
| **Cloudflare** | CDN, DDoS protection, DNS | Free tier (unlimited requests) |
| **Railway.app** | Temporary staging environments | $5 free credit/month |
| **Better Uptime** | Uptime monitoring, status page | Free tier: 10 monitors |
| **Plausible** | GDPR-compliant analytics | Self-hosted (free) |

---

## 🚢 Deployment

### Production Deployment (DigitalOcean)

#### 1. Prepare Droplet

```bash
# Create droplet via UI or CLI
doctl compute droplet create ai-receptionist \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys your-ssh-key-id

# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y
```

#### 2. Clone & Configure

```bash
# Clone repo
git clone https://github.com/montaassarr/ai-_receptionist.git
cd ai-_receptionist

# Create production .env
cp backend/.env.example backend/.env
nano backend/.env  # Edit with production values

# Update CORS to include production domain
CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]
```

#### 3. Deploy with Docker Compose

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

#### 4. Configure Nginx

```bash
# Install Nginx
apt install nginx -y

# Create config
nano /etc/nginx/sites-available/ai-receptionist
```

Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/ai-receptionist /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 5. Setup SSL (Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificates
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal is configured automatically
```

#### 6. Configure Webhooks

Update webhook URLs in:
- **Vapi Dashboard**: https://api.yourdomain.com/api/v1/voice/webhook
- **Meta Developer Console**: https://api.yourdomain.com/api/v1/webhook

---

## 📚 API Reference

### Base URL

```
Production: https://api.yourdomain.com/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication

Most endpoints require JWT token. Obtain via `/users/login`:

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use token in subsequent requests:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/appointments/
```

### Endpoints

#### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/appointments/` | Create appointment |
| `GET` | `/appointments/` | List appointments (paginated) |
| `GET` | `/appointments/{id}` | Get single appointment |
| `PUT` | `/appointments/{id}` | Update appointment |
| `DELETE` | `/appointments/{id}` | Cancel appointment |
| `GET` | `/appointments/stats/summary` | Get statistics |

**Example: Create Appointment**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "client_name": "John Doe",
    "client_phone": "+11234567890",
    "service_name": "Haircut",
    "scheduled_time": "2025-11-25T15:00:00",
    "duration_minutes": 30,
    "notes": "Prefer senior stylist"
  }'
```

#### Voice Agent

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/voice/config` | Get voice configuration |
| `PUT` | `/voice/config` | Update voice configuration |
| `GET` | `/voice/vapi-config` | Get Vapi public key + assistant ID |
| `GET` | `/voice/call-history` | Get call logs |
| `POST` | `/voice/webhook` | Vapi webhook receiver (internal) |
| `GET` | `/voice/models` | List available LLM models |
| `GET` | `/voice/voices` | List available TTS voices |
| `GET` | `/voice/tools` | List available tools |

**Example: Update Voice Config**
```bash
curl -X PUT http://localhost:8000/api/v1/voice/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "model_provider": "groq",
    "model_name": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "voice_provider": "11labs",
    "voice_id": "rachel",
    "first_message": "Hello, this is Ava. How may I help you?",
    "system_prompt": "You are a friendly receptionist...",
    "enabled_tools": ["check_availability", "book_appointment", "get_services"],
    "end_call_on_goodbye": true,
    "record_calls": true,
    "silence_timeout_seconds": 30
  }'
```

#### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/conversations/` | List conversations |
| `GET` | `/conversations/{id}` | Get conversation transcript |
| `DELETE` | `/conversations/{id}` | Delete conversation |

#### Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/services/` | Create service |
| `GET` | `/services/` | List services |
| `GET` | `/services/{id}` | Get service |
| `PUT` | `/services/{id}` | Update service |
| `DELETE` | `/services/{id}` | Deactivate service |

#### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/register` | Register new user |
| `POST` | `/users/login` | Login (get JWT token) |
| `GET` | `/users/me` | Get current user |
| `PUT` | `/users/me` | Update current user |

#### Business Config

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/business/config` | Get business configuration |
| `PUT` | `/business/config` | Update business configuration |

**Full API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc).**

---

## 🗺️ Roadmap (6-Month Plan)

### 📍 Phase 1: MVP (Months 1-2)

**Goal:** Launch functional WhatsApp + Voice booking system

- [x] Backend API (FastAPI)
  - [x] Appointment CRUD
  - [x] User authentication
  - [x] Business configuration
  - [x] Conversation state management
- [x] WhatsApp Integration
  - [x] Meta Cloud API webhook
  - [x] Groq-powered conversation
  - [x] Intent classification
  - [x] Entity extraction
- [x] Voice Agent (Vapi)
  - [x] Assistant creation API
  - [x] Tool execution (book, cancel, check availability)
  - [x] Webhook processing
  - [x] Call recording
- [x] Admin Dashboard
  - [x] Login/auth
  - [x] Appointment management
  - [x] Conversation viewer
  - [x] Service management
  - [x] Voice settings page
- [x] Database
  - [x] MongoDB schema design
  - [x] Indexes for performance
  - [x] Conversation persistence
- [x] Deployment
  - [x] Docker Compose
  - [x] Environment configuration
  - [x] Basic monitoring

### 📍 Phase 2: SaaS Polish (Months 3-4)

**Goal:** Multi-tenant SaaS with billing

- [ ] Multi-Tenancy
  - [ ] Business ID isolation
  - [ ] Tenant onboarding flow
  - [ ] Subdomain routing (`client1.yourdomain.com`)
  - [ ] White-label branding options
- [ ] Payment System
  - [ ] Stripe integration
  - [ ] Subscription tiers (Starter, Pro, Enterprise)
  - [ ] Usage-based billing (per call/message)
  - [ ] Invoice generation
  - [ ] Payment webhooks
- [ ] User Management
  - [ ] Role-based access control (Admin, Manager, Viewer)
  - [ ] Team invitations
  - [ ] Audit logs
- [ ] Enhanced Dashboard
  - [ ] Real-time WebSocket updates
  - [ ] Advanced analytics (conversion rates, peak hours)
  - [ ] Revenue tracking
  - [ ] Customer insights
- [ ] Notifications
  - [ ] Email confirmations (via SendGrid)
  - [ ] SMS reminders (via Twilio)
  - [ ] Webhook notifications to third-party systems
- [ ] API Improvements
  - [ ] Rate limiting per tenant
  - [ ] API key generation for customers
  - [ ] Webhooks for external integrations

### 📍 Phase 3: Enterprise Features (Months 5-6)

**Goal:** Advanced features for large clients

- [ ] Advanced Analytics
  - [ ] Call sentiment analysis (Groq + custom models)
  - [ ] Conversion funnel tracking
  - [ ] Agent performance scoring
  - [ ] Predictive booking trends
  - [ ] Export reports (CSV, PDF)
- [ ] Custom Voice Models
  - [ ] Voice cloning (ElevenLabs Professional Voice Cloning)
  - [ ] Brand-specific voices
  - [ ] Multi-language support (Spanish, French, Mandarin)
  - [ ] Accent customization
- [ ] Auto-Translation
  - [ ] Detect caller language
  - [ ] Translate conversations in real-time
  - [ ] Store transcripts in original + translated
- [ ] IVR Menu System
  - [ ] Multi-level phone trees
  - [ ] Keypad input handling
  - [ ] Department routing
  - [ ] Queue management
  - [ ] Hold music configuration
- [ ] Integrations
  - [ ] Google Calendar sync (two-way)
  - [ ] Outlook Calendar sync
  - [ ] Zapier webhooks
  - [ ] Slack notifications
  - [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Mobile App (React Native)
  - [ ] iOS + Android
  - [ ] Push notifications
  - [ ] Quick actions (approve/reject bookings)
  - [ ] In-app call testing
- [ ] Advanced Security
  - [ ] HIPAA compliance mode (for healthcare clients)
  - [ ] SOC 2 Type II audit
  - [ ] Data encryption at rest
  - [ ] Penetration testing
- [ ] Performance Optimization
  - [ ] Edge caching (Cloudflare Workers)
  - [ ] Database sharding for scale
  - [ ] Redis Cluster for caching
  - [ ] CDN for static assets

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Branch Workflow

```bash
# Fork the repo on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-_receptionist.git
cd ai-_receptionist

# Add upstream remote
git remote add upstream https://github.com/montaassarr/ai-_receptionist.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "feat: Add amazing feature"

# Push to your fork
git push origin feature/your-feature-name

# Open Pull Request on GitHub
```

### Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Add or update tests
- `chore:` Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add voice recording toggle in settings"
git commit -m "fix: Prevent double-booking on same time slot"
git commit -m "docs: Update API reference for voice endpoints"
```

### Pull Request Rules

1. **Title:** Use conventional commit format
2. **Description:** Explain what and why (not how)
3. **Tests:** Add tests for new features
4. **Lint:** Run `black backend/` and `eslint frontend/src` before pushing
5. **Docs:** Update README or docs if needed
6. **Small PRs:** Keep changes focused (one feature per PR)

### Testing Standards

**Backend (Pytest):**
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_appointments.py

# Run specific test
pytest tests/test_appointments.py::test_create_appointment
```

**Frontend (Jest):**
```bash
cd frontend
npm run test

# Coverage
npm run test -- --coverage
```

**Code Quality:**
```bash
# Python
black backend/
flake8 backend/
mypy backend/

# TypeScript
npm run lint
npm run type-check
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Montassar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🆘 Support

### Documentation

- **[Setup Guide](INSTALLATION.md)** - Detailed installation instructions
- **[API Reference](#-api-reference)** - Endpoint documentation
- **[Voice Agent Demo](VOICE_AGENT_LOCAL_DEMO.md)** - Test voice features locally
- **[Database Schema](docs/database_schema.md)** - MongoDB collections
- **[Architecture](docs/ARCHITECTURE.md)** - System design deep-dive

### Community & Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/montaassarr/ai-_receptionist/issues)
- **Discussions:** [Ask questions, share ideas](https://github.com/montaassarr/ai-_receptionist/discussions)
- **Email:** contact@yourdomain.com

### Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**MongoDB connection errors:**
```bash
# Local MongoDB
sudo systemctl status mongod
sudo systemctl start mongod

# Atlas - check firewall, IP whitelist
```

**WhatsApp webhook not receiving:**
```bash
# Check ngrok is running
ngrok http 8000

# Verify webhook URL in Meta Developer Console
# Test webhook manually:
curl -X POST https://your-ngrok-url.ngrok.io/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{"object": "whatsapp_business_account", "entry": []}'
```

**Voice agent errors:**
```bash
# Check Vapi API key
echo $VAPI_API_KEY

# Test assistant creation
python backend/scripts/voice_crud_demo.py

# View logs
tail -f backend/logs/app.log
```

---

## 🎯 Quick Links

- **Live Demo:** https://demo.yourdomain.com
- **Documentation:** https://docs.yourdomain.com
- **API Docs:** https://api.yourdomain.com/docs
- **GitHub:** https://github.com/montaassarr/ai-_receptionist
- **Issues:** https://github.com/montaassarr/ai-_receptionist/issues
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 🌟 Sponsors & Credits

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [Vapi](https://vapi.ai/) - Voice AI infrastructure
- [Groq](https://groq.com/) - LLM inference
- [ElevenLabs](https://elevenlabs.io/) - Voice synthesis
- [Twilio](https://www.twilio.com/) - Phone numbers & SMS
- [Meta](https://developers.facebook.com/) - WhatsApp Cloud API

### Acknowledgments

- **GitHub Student Developer Pack** for providing free credits
- **DigitalOcean** for cloud hosting
- **MongoDB Atlas** for database infrastructure
- All open-source contributors

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/montaassarr/ai-_receptionist?style=social)
![GitHub forks](https://img.shields.io/github/forks/montaassarr/ai-_receptionist?style=social)
![GitHub issues](https://img.shields.io/github/issues/montaassarr/ai-_receptionist)
![GitHub pull requests](https://img.shields.io/github/issues-pr/montaassarr/ai-_receptionist)
![GitHub last commit](https://img.shields.io/github/last-commit/montaassarr/ai-_receptionist)

---

<p align="center">
  <strong>Built with ❤️ for businesses worldwide</strong><br>
  <sub>AI Voice + WhatsApp Receptionist SaaS Platform</sub>
</p>

<p align="center">
  <a href="https://github.com/montaassarr/ai-_receptionist">⭐ Star on GitHub</a> •
  <a href="https://github.com/montaassarr/ai-_receptionist/issues/new">🐛 Report Bug</a> •
  <a href="https://github.com/montaassarr/ai-_receptionist/issues/new">💡 Request Feature</a>
</p>

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

---

```bash

**Made with ❤️ for barbershops worldwide**# Build and run with Docker Compose

docker-compose up -d

---

# View logs

## Quick Linksdocker-compose logs -f



- [Installation](INSTALLATION.md)# Stop services

- [API Docs](http://localhost:8000/docs)docker-compose down

- [GitHub](https://github.com/montaassarr/ai-_receptionist)```

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
