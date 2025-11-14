# 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + TS)                        │
│                     http://localhost:8080                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    │ Bearer Token Auth
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API INTEGRATION LAYER                             │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  auth.ts    │  │appointments │  │conversations│  │ services  │ │
│  │             │  │    .ts      │  │    .ts      │  │   .ts     │ │
│  │ - login()   │  │ - list()    │  │ - list()    │  │ - list()  │ │
│  │ - register()│  │ - create()  │  │ - get()     │  │ - create()│ │
│  │ - logout()  │  │ - update()  │  │ - search()  │  │ - update()│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
│                                                                       │
│  ┌─────────────┐  ┌─────────────────────────────────────────────┐  │
│  │ webhook.ts  │  │         lib/api.ts (Axios)                  │  │
│  │             │  │  - Interceptor adds Bearer token            │  │
│  │ - getStatus │  │  - Auto-redirect on 401                     │  │
│  └─────────────┘  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ axios.get/post/put/delete
                                    │ /api/v1/*
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                         │
│                     http://localhost:8000                            │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      ROUTERS (API Endpoints)                    │ │
│  │                                                                  │ │
│  │  /api/v1/users         /api/v1/appointments                    │ │
│  │  ├─ POST /login         ├─ GET /                               │ │
│  │  ├─ POST /register      ├─ POST /                              │ │
│  │  ├─ GET /me             ├─ GET /{id}                           │ │
│  │  └─ GET /               ├─ PUT /{id}                           │ │
│  │                         └─ DELETE /{id}                         │ │
│  │                                                                  │ │
│  │  /api/v1/conversations  /api/v1/services                       │ │
│  │  ├─ GET /               ├─ GET /                               │ │
│  │  └─ GET /{id}           ├─ POST /                              │ │
│  │                         ├─ PUT /{id}                           │ │
│  │  /api/v1/webhook        └─ DELETE /{id}                        │ │
│  │  ├─ POST /sms                                                   │ │
│  │  ├─ POST /voice                                                 │ │
│  │  └─ GET /status                                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                    │                                 │
│                                    ▼                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     AI LAYER (Groq Agent)                       │ │
│  │                                                                  │ │
│  │  ┌──────────────────┐  ┌───────────────────┐                  │ │
│  │  │ ConversationMgr  │  │   Groq Agent      │                  │ │
│  │  │                  │  │                   │                  │ │
│  │  │ - process_msg()  │──│ - generate_res()  │                  │ │
│  │  │ - classify_int() │  │ - classify_int()  │                  │ │
│  │  │ - extract_ent()  │  │ - extract_ent()   │                  │ │
│  │  └──────────────────┘  └───────────────────┘                  │ │
│  │          │                       │                              │ │
│  │          │                       ▼                              │ │
│  │          │              Groq API (Mixtral-8x7b)                │ │
│  │          ▼                                                       │ │
│  │   Auto-create appointments in DB                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                    │                                 │
│                                    ▼                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    DATABASE LAYER (MongoDB)                     │ │
│  │                                                                  │ │
│  │  Collections:                                                    │ │
│  │  ├─ users          (admin, staff)                              │ │
│  │  ├─ appointments   (bookings with client info)                 │ │
│  │  ├─ conversations  (AI chat history + state)                   │ │
│  │  └─ services       (haircut, fade, etc.)                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    │ Webhooks
                                    │
┌─────────────────────────────────────────────────────────────────────┐
│                         TWILIO (SMS/Voice)                           │
│                                                                       │
│  Customer sends SMS ──────┬─────────────────────────────────────┐  │
│                            │                                      │  │
│                            ▼                                      │  │
│                  POST /api/v1/webhook/sms                        │  │
│                            │                                      │  │
│                            ▼                                      │  │
│                  AI processes & responds                         │  │
│                            │                                      │  │
│                            ▼                                      │  │
│                  Twilio sends SMS response ──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Customer Books Appointment via SMS

```
1. Customer: "I want to book a haircut tomorrow at 2pm"
   │
   ▼
2. Twilio receives SMS → POST /webhook/sms
   │
   ▼
3. ConversationManager.process_message()
   │
   ├─ Get/create conversation from MongoDB
   │
   ├─ ClassifyIntent → "book_appointment"
   │
   ├─ ExtractEntities → service="haircut", datetime="tomorrow 2pm"
   │
   ├─ GroqAgent.generate_response()
   │   │
   │   └─ Groq API (Mixtral) → "Great! Let me book that for you..."
   │
   ├─ IF all info collected:
   │   └─ Create appointment in MongoDB
   │       └─ Send SMS confirmation via Twilio
   │
   └─ Save conversation state
   │
   ▼
4. AI Response: "Perfect! I've booked your haircut for tomorrow at 2pm..."
   │
   ▼
5. Dashboard updates automatically (React Query refetch)
```

---

## Frontend Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         App.tsx                               │
│                    (Router + Auth)                            │
└──────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
      ┌─────────┐       ┌─────────┐       ┌─────────┐
      │  Login  │       │Protected│       │ NotFound│
      │  Page   │       │ Routes  │       │  Page   │
      └─────────┘       └─────────┘       └─────────┘
                              │
           ┌──────────────────┼──────────────────┬──────────────┐
           ▼                  ▼                  ▼              ▼
      ┌─────────┐       ┌──────────┐      ┌──────────┐  ┌──────────┐
      │Dashboard│       │Appoint-  │      │Conversa- │  │ Services │
      │  (/)    │       │ ments    │      │ tions    │  │          │
      └─────────┘       └──────────┘      └──────────┘  └──────────┘
           │
           ▼
      Each page uses:
      ├─ Sidebar (navigation)
      ├─ DashboardHeader (user info)
      ├─ useQuery (data fetching)
      ├─ API services (appointments, conversations, etc.)
      └─ Shadcn UI components (Button, Input, Card, etc.)
```

---

## Authentication Flow

```
User enters credentials
         │
         ▼
    Login.tsx
         │
         │ authApi.login(credentials)
         ▼
    FormData sent to /api/v1/users/token
         │
         ▼
    Backend verifies username/password (argon2)
         │
         ├─ Invalid → 401 Unauthorized
         │
         └─ Valid → Create JWT token
                    │
                    ▼
              Return { access_token, token_type }
                    │
                    ▼
         localStorage.setItem('access_token', token)
                    │
                    ▼
         Navigate to dashboard (/)
                    │
                    ▼
         ProtectedRoute checks token exists
                    │
                    ├─ No token → Redirect to /login
                    │
                    └─ Has token → Render page
                              │
                              ▼
         api.ts interceptor adds "Bearer {token}" to all requests
```

---

## Real-time Data Sync

```
Dashboard loads
      │
      ▼
useQuery({ queryKey: ["appointments"], queryFn: appointmentsApi.list })
      │
      ├─ Check cache
      │   ├─ Hit → Return cached data
      │   └─ Miss → Fetch from backend
      │
      ▼
GET /api/v1/appointments
      │
      ▼
FastAPI → MongoDB query
      │
      ▼
Return AppointmentResponse[]
      │
      ▼
React Query:
  ├─ Cache data
  ├─ Display in UI
  └─ Auto-refetch every 5 minutes (default)

When user creates appointment:
      │
      ▼
useMutation({ mutationFn: appointmentsApi.create })
      │
      ▼
POST /api/v1/appointments
      │
      ▼
Backend creates in MongoDB + sends SMS
      │
      ▼
queryClient.invalidateQueries(["appointments"])
      │
      ▼
Automatic refetch → Dashboard updates
```

---

## File Organization

```
ai_receptionist/
│
├── backend/                    # FastAPI server
│   ├── main.py                # Entry point + routes
│   ├── routers/               # API endpoints
│   │   ├── users.py
│   │   ├── appointments.py
│   │   ├── conversations.py
│   │   ├── services.py
│   │   └── webhook.py
│   ├── models/                # Pydantic models
│   ├── ai/                    # Groq agent + conversation manager
│   └── database/              # MongoDB config
│
├── frontend/                  # React app
│   ├── src/
│   │   ├── api/              # API service layer ✨ NEW
│   │   ├── lib/              # Utilities + types
│   │   ├── pages/            # Route pages ✨ UPDATED
│   │   ├── components/       # Reusable UI
│   │   └── App.tsx           # Router ✨ UPDATED
│   └── package.json
│
└── docs/                      # Documentation
    ├── BACKEND_FRONTEND_MAPPING.md      ✨ NEW
    ├── FRONTEND_INTEGRATION_GUIDE.md    ✨ NEW
    └── FRONTEND_RESTRUCTURE_SUMMARY.md  ✨ NEW
```

---

**This diagram shows how everything connects from customer SMS to dashboard display! 🎯**
