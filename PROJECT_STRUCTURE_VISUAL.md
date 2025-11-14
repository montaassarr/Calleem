# 📁 Complete Project Structure - Visual Reference

## 🎯 Quick Navigation

```
ai_receptionist/
│
├── 📖 DOCUMENTATION (Start Here!)
│   ├── COMPLETE_SETUP_GUIDE.md          ⭐ STEP-BY-STEP SETUP
│   ├── FINAL_COMPLETION_SUMMARY.md      ⭐ WHAT WAS BUILT
│   ├── QUICK_START.md                   ⭐ 30-SECOND START
│   ├── BACKEND_FRONTEND_MAPPING.md      (API reference)
│   ├── FRONTEND_INTEGRATION_GUIDE.md    (Patterns & best practices)
│   ├── ARCHITECTURE_DIAGRAM.md          (System architecture)
│   └── PROJECT_SUMMARY.md               (Original docs)
│
├── 🔧 BACKEND (Python/FastAPI)
│   ├── main.py                          🚀 START BACKEND HERE
│   ├── create_admin.py                  (Create first admin user)
│   ├── requirements.txt                 (Python dependencies)
│   ├── .env                             (Config - CREATE THIS!)
│   │
│   ├── 📂 routers/                      (API endpoints)
│   │   ├── appointments.py              (Appointments CRUD)
│   │   ├── services.py                  (Services CRUD)
│   │   ├── users.py                     (Users CRUD + auth)
│   │   ├── webhook.py                   (Twilio webhook)
│   │   └── __init__.py
│   │
│   ├── 📂 models/                       (MongoDB schemas)
│   │   ├── appointment.py
│   │   ├── service.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── __init__.py
│   │
│   ├── 📂 ai/                           (AI/NLP logic)
│   │   ├── groq_agent.py                (Groq AI integration)
│   │   ├── conversation_manager.py      (Conversation flow)
│   │   ├── intents.py                   (Intent detection)
│   │   └── prompt_templates.py
│   │
│   ├── 📂 database/
│   │   └── mongo_config.py              (MongoDB connection)
│   │
│   └── 📂 utils/
│       ├── config.py                    (Environment config)
│       ├── twilio_handler.py            (Twilio integration)
│       └── datetime_utils.py
│
├── 💻 FRONTEND (React/TypeScript)
│   ├── package.json                     (Dependencies)
│   ├── vite.config.js                   (Build config)
│   ├── tailwind.config.js               (Styling config)
│   │
│   ├── 📂 src/
│   │   ├── App.tsx                      🎯 ROUTING (15+ routes)
│   │   ├── main.tsx                     (Entry point)
│   │   ├── index.css                    (Global styles)
│   │   │
│   │   ├── 📂 components/               🧩 REUSABLE COMPONENTS
│   │   │   ├── AppointmentFormModal.tsx ⭐ NEW - Appointment CRUD
│   │   │   ├── ServiceFormModal.tsx     ⭐ NEW - Service CRUD
│   │   │   ├── Sidebar.tsx              (Navigation)
│   │   │   ├── DashboardHeader.tsx      (Top header)
│   │   │   ├── ProtectedRoute.tsx       (Auth wrapper)
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Navbar.tsx
│   │   │
│   │   ├── 📂 pages/                    📄 ALL PAGES (14 NEW)
│   │   │   ├── Index.tsx                (Dashboard)
│   │   │   ├── Login.tsx                (Authentication)
│   │   │   ├── NotFound.tsx             (404 page)
│   │   │   │
│   │   │   ├── Appointments.tsx         ⭐ UPDATED - Full CRUD
│   │   │   ├── Conversations.tsx        (Chat history)
│   │   │   ├── Services.tsx             ⭐ UPDATED - Full CRUD
│   │   │   ├── Schedule.tsx             ⭐ NEW - FullCalendar
│   │   │   ├── WhatsApp.tsx             (Webhook status)
│   │   │   ├── Help.tsx                 ⭐ NEW - FAQ & resources
│   │   │   │
│   │   │   ├── 📂 AIReceptionist/
│   │   │   │   ├── Index.tsx            ⭐ NEW - AI overview
│   │   │   │   └── Test.tsx             ⭐ NEW - AI chat simulator
│   │   │   │
│   │   │   └── 📂 Settings/             ⭐ ALL NEW
│   │   │       ├── Index.tsx            (Settings hub)
│   │   │       ├── Business.tsx         (Company profile)
│   │   │       ├── Team.tsx             (User CRUD)
│   │   │       ├── AI.tsx               (AI config)
│   │   │       └── Integrations.tsx     (API keys)
│   │   │
│   │   ├── 📂 api/                      🌐 API SERVICE LAYER
│   │   │   ├── auth.ts                  (authApi, usersApi)
│   │   │   ├── appointments.ts          (appointmentsApi)
│   │   │   ├── services.ts              (servicesApi)
│   │   │   ├── conversations.ts         (conversationsApi)
│   │   │   ├── webhook.ts               (webhookApi)
│   │   │   └── index.ts                 (Centralized exports)
│   │   │
│   │   └── 📂 lib/
│   │       ├── types.ts                 📋 46 TYPESCRIPT INTERFACES
│   │       └── api.js                   (Axios config)
│   │
│   └── 📂 public/                       (Static assets)
│
├── 🗄️ DATABASE
│   └── MongoDB                          (Install separately)
│       └── Database: ai_receptionist
│           ├── users
│           ├── appointments
│           ├── services
│           └── conversations
│
└── 🐳 DOCKER (Optional)
    ├── docker-compose.yml               (Multi-container setup)
    ├── backend/Dockerfile
    └── frontend/Dockerfile (if created)
```

---

## 🎨 Component Architecture

```
┌─────────────────────────────────────────┐
│           Browser (Chrome)              │
│  http://localhost:5173                  │
└──────────────┬──────────────────────────┘
               │
       ┌───────▼────────┐
       │   App.tsx      │  (Routes)
       └───────┬────────┘
               │
    ┌──────────┼──────────┐
    │                     │
┌───▼────┐         ┌─────▼──────┐
│Sidebar │         │   Pages    │
└────────┘         └─────┬──────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼───┐  ┌──▼───┐  ┌──▼────┐
         │Dashboard│ │Appts │  │Service│
         └────┬────┘ └──┬───┘  └──┬────┘
              │         │         │
         ┌────▼──────┐  │    ┌────▼──────┐
         │useQuery   │  │    │useMutation│
         │(React Q)  │  │    │(React Q)  │
         └────┬──────┘  │    └────┬──────┘
              │         │         │
         ┌────▼─────────▼─────────▼────┐
         │     API Service Layer       │
         │  (appointments, services)   │
         └────┬────────────────────────┘
              │
         ┌────▼────────┐
         │   Axios     │ (HTTP client)
         └────┬────────┘
              │
   ┌──────────▼──────────┐
   │  Backend (FastAPI)  │
   │  http://localhost   │
   │       :8000         │
   └──────────┬──────────┘
              │
         ┌────▼────────┐
         │   MongoDB   │
         └─────────────┘
```

---

## 📊 Data Flow Example: Create Appointment

```
1. USER ACTION
   Click "New Appointment" button

2. COMPONENT STATE
   Appointments.tsx → setIsModalOpen(true)

3. MODAL RENDER
   AppointmentFormModal.tsx opens

4. FORM SUBMISSION
   User fills form → clicks "Create"

5. MUTATION
   createMutation.mutate(formData)

6. API CALL
   appointmentsApi.create(data)
   → POST http://localhost:8000/api/v1/appointments

7. BACKEND
   FastAPI router → MongoDB insert

8. RESPONSE
   { id: "123", client_name: "John", ... }

9. CACHE UPDATE
   React Query invalidates ["appointments"]

10. UI UPDATE
    Table re-fetches → new appointment appears

11. NOTIFICATION
    toast.success("Appointment created!")

12. MODAL CLOSE
    setIsModalOpen(false)
```

---

## 🔑 Key Features by File

### `App.tsx`
- **Lines 1-20**: Imports (14 pages + components)
- **Lines 22-28**: QueryClient + auth setup
- **Lines 30-140**: Route definitions (15 routes)
- **Features**: Protected routes, 404 handling

### `Appointments.tsx`
- **Lines 1-25**: Imports + modal state
- **Lines 27-52**: API queries & mutations
- **Lines 54-80**: CRUD handlers
- **Lines 82-150**: Table UI
- **Lines 152-180**: AppointmentFormModal + DeleteDialog
- **Features**: Create, edit, delete with modals

### `Services.tsx`
- **Lines 1-25**: Imports + modal state
- **Lines 27-80**: API queries, mutations, handlers
- **Lines 82-200**: Card grid UI with switches
- **Lines 202-230**: ServiceFormModal + DeleteDialog
- **Features**: CRUD + active/inactive toggle

### `AppointmentFormModal.tsx`
- **Lines 1-50**: Form state setup
- **Lines 52-75**: Pre-fill logic for edit mode
- **Lines 77-120**: Create/update mutations
- **Lines 122-230**: Form UI (7 fields)
- **Features**: Reusable create/edit modal

### `ServiceFormModal.tsx`
- **Lines 1-50**: Form state setup
- **Lines 52-110**: CRUD mutations
- **Lines 112-210**: Form UI (5 fields + checkbox)
- **Features**: Reusable create/edit modal

### `types.ts`
- **Lines 1-50**: User & auth types
- **Lines 52-95**: Appointment types
- **Lines 97-140**: Conversation types
- **Lines 142-165**: Service types
- **Lines 167-281**: Calendar, webhook, filter types
- **Features**: 46 interfaces, full type safety

---

## 🛠️ Development Workflow

### Adding a New Feature

```
1. DESIGN
   └─ Sketch UI mockup
   └─ Plan API endpoints needed

2. BACKEND
   └─ Create model in backend/models/
   └─ Create router in backend/routers/
   └─ Test in http://localhost:8000/docs

3. FRONTEND TYPES
   └─ Add interfaces to src/lib/types.ts

4. API SERVICE
   └─ Create service file in src/api/
   └─ Export in src/api/index.ts

5. COMPONENT
   └─ Create page in src/pages/
   └─ Use useQuery/useMutation
   └─ Add UI with Shadcn components

6. ROUTING
   └─ Add route in src/App.tsx
   └─ Add nav link in Sidebar.tsx

7. TEST
   └─ Run both servers
   └─ Click through UI
   └─ Check browser console
   └─ Verify data in MongoDB

8. COMMIT
   └─ git add .
   └─ git commit -m "Add feature X"
   └─ git push
```

---

## 📦 Package Management

### Frontend Dependencies
```json
{
  "Main": [
    "react@18",
    "react-router-dom@6",
    "@tanstack/react-query@5",
    "axios@1"
  ],
  "UI": [
    "@radix-ui/react-*",
    "tailwindcss",
    "lucide-react"
  ],
  "Calendar": [
    "@fullcalendar/react",
    "@fullcalendar/daygrid",
    "@fullcalendar/timegrid",
    "@fullcalendar/interaction"
  ],
  "Utils": [
    "sonner",
    "date-fns",
    "clsx"
  ]
}
```

### Backend Dependencies
```
FastAPI
uvicorn
pymongo
motor
python-jose
passlib
twilio
groq
python-dotenv
pydantic
```

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend Dev | http://localhost:5173 | Main app |
| Backend API | http://localhost:8000 | API server |
| Swagger UI | http://localhost:8000/docs | API docs |
| ReDoc | http://localhost:8000/redoc | Alt API docs |
| MongoDB | mongodb://localhost:27017 | Database |

---

## 🎯 File Count Summary

### Created This Session
- **Pages**: 14 new + 7 updated = 21 total
- **Components**: 2 new modals
- **API Services**: 6 complete files
- **Documentation**: 6 comprehensive guides
- **Types**: 46 TypeScript interfaces
- **Routes**: 15 in App.tsx

### Total Project
- **Frontend Files**: 50+ TypeScript/TSX files
- **Backend Files**: 30+ Python files
- **Documentation**: 15+ markdown files
- **Config Files**: 10+ (package.json, vite.config, etc.)

---

## ✨ Quick Tips

### Find Something Fast
```bash
# Find all pages
ls frontend/src/pages/

# Find all API services
ls frontend/src/api/

# Find all components
ls frontend/src/components/

# Search for text
grep -r "AppointmentFormModal" frontend/src/
```

### Common Paths
```
Dashboard:     frontend/src/pages/Index.tsx
Appointments:  frontend/src/pages/Appointments.tsx
API Layer:     frontend/src/api/*
Types:         frontend/src/lib/types.ts
Routing:       frontend/src/App.tsx
Backend API:   backend/routers/*
Models:        backend/models/*
```

---

**🎉 Use this as your map! Everything you need is documented here.**

_Last updated: January 2025_
