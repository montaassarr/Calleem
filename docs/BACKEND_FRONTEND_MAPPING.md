# Backend → Frontend Mapping
**Complete API & Dashboard Integration Guide**

---

## 📌 Backend API Structure

### Base URL: `http://localhost:8000/api/v1`

---

## 🔐 1. AUTHENTICATION & USERS
**Route Prefix:** `/api/v1/users`

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/users/register` | POST | Register new user | `UserCreate` | `UserResponse` |
| `/users/login` | POST | User login | `OAuth2PasswordRequestForm` | `Token` |
| `/users/token` | POST | OAuth2 token (alias) | `OAuth2PasswordRequestForm` | `Token` |
| `/users/me` | GET | Get current user | - | `UserResponse` |
| `/users/{user_id}` | GET | Get user by ID | - | `UserResponse` |
| `/users/` | GET | List all users | - | `List[UserResponse]` |
| `/users/{user_id}` | PUT | Update user | `UserUpdate` | `UserResponse` |
| `/users/{user_id}` | DELETE | Delete user | - | 204 No Content |

**Models:**
```typescript
interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role?: string; // "admin" | "staff"
  active?: boolean;
}

interface UserResponse {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  active: boolean;
  created_at: string;
  last_login?: string;
}

interface Token {
  access_token: string;
  token_type: string;
}
```

---

## 📅 2. APPOINTMENTS
**Route Prefix:** `/api/v1/appointments`

| Endpoint | Method | Purpose | Query Params | Request Body | Response |
|----------|--------|---------|--------------|--------------|----------|
| `/appointments/` | POST | Create appointment | - | `AppointmentCreate` | `AppointmentResponse` |
| `/appointments/` | GET | List appointments | `status`, `date_from`, `date_to`, `client_phone`, `skip`, `limit` | - | `List[AppointmentResponse]` |
| `/appointments/{id}` | GET | Get appointment | - | - | `AppointmentResponse` |
| `/appointments/{id}` | PUT | Update appointment | - | `AppointmentUpdate` | `AppointmentResponse` |
| `/appointments/{id}` | DELETE | Delete appointment | - | - | 204 No Content |

**Models:**
```typescript
interface AppointmentCreate {
  client_name: string;
  client_phone: string;
  service: string;
  datetime: string; // ISO datetime
  duration_minutes: number;
  notes?: string;
}

interface AppointmentUpdate {
  client_name?: string;
  service?: string;
  datetime?: string;
  duration_minutes?: number;
  status?: "confirmed" | "cancelled" | "completed" | "no_show";
  notes?: string;
}

interface AppointmentResponse {
  id: string;
  client_name: string;
  client_phone: string;
  service: string;
  datetime: string;
  duration_minutes: number;
  status: "confirmed" | "cancelled" | "completed" | "no_show";
  notes?: string;
  created_at: string;
  updated_at: string;
}
```

---

## 💬 3. CONVERSATIONS
**Route Prefix:** `/api/v1/conversations`

| Endpoint | Method | Purpose | Query Params | Response |
|----------|--------|---------|--------------|----------|
| `/conversations/` | GET | List conversations | `search`, `limit` | `List[ConversationResponse]` |
| `/conversations/{id}` | GET | Get conversation | - | `ConversationResponse` |

**Models:**
```typescript
interface Message {
  role: "client" | "ai";
  text: string;
  timestamp: string;
  metadata?: any;
}

interface ConversationState {
  intent: string;
  collected_info: {
    service?: string;
    datetime?: string;
    client_name?: string;
    phone_number?: string;
  };
  awaiting_field?: string;
}

interface ConversationResponse {
  id: string;
  conversation_id: string;
  phone_number: string;
  messages: Message[];
  state: ConversationState;
  status: string;
  created_at: string;
  updated_at: string;
}
```

---

## ✂️ 4. SERVICES
**Route Prefix:** `/api/v1/services`

| Endpoint | Method | Purpose | Query Params | Request Body | Response |
|----------|--------|---------|--------------|--------------|----------|
| `/services/` | POST | Create service | - | `ServiceCreate` | `ServiceResponse` |
| `/services/` | GET | List services | `active_only`, `skip`, `limit` | - | `List[ServiceResponse]` |
| `/services/{id}` | GET | Get service | - | - | `ServiceResponse` |
| `/services/{id}` | PUT | Update service | - | `ServiceUpdate` | `ServiceResponse` |
| `/services/{id}` | DELETE | Delete service | - | - | 204 No Content |

**Models:**
```typescript
interface ServiceCreate {
  name: string;
  description: string;
  duration_minutes: number;
  price: number;
  active?: boolean;
}

interface ServiceUpdate {
  name?: string;
  description?: string;
  duration_minutes?: number;
  price?: number;
  active?: boolean;
}

interface ServiceResponse {
  id: string;
  name: string;
  description: string;
  duration_minutes: number;
  price: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}
```

---

## 📞 5. TWILIO WEBHOOK
**Route Prefix:** `/api/v1/webhook`

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/webhook/sms` | POST | Handle incoming SMS | Twilio webhook only |
| `/webhook/voice` | POST | Handle incoming calls | Twilio webhook only |
| `/webhook/voice/menu` | POST | Handle voice menu | Twilio webhook only |
| `/webhook/status` | GET | Webhook status | Public endpoint |

**Response:**
```typescript
interface WebhookStatus {
  status: "active";
  endpoints: {
    sms: string;
    voice: string;
    voice_menu: string;
  };
}
```

---

## 🏪 6. BUSINESS SETTINGS
**Managed via:** Environment Variables & Settings

**Available via:** `settings.py` / Configuration API (if exposed)

```typescript
interface BusinessSettings {
  business_name: string;
  business_phone: string;
  business_email: string;
  business_address: string;
  business_hours: string;
  timezone: string;
  available_services: string; // comma-separated
}
```

---

## 🎯 Frontend Dashboard Structure

### Required Pages & Routes

```
/                           → Dashboard Overview
/ai-receptionist            → AI Chat Interface & Settings
/ai-receptionist/test       → Live Chat Tester
/appointments               → Appointments List & Calendar
/appointments/new           → Create Appointment
/appointments/:id           → View/Edit Appointment
/conversations              → Conversation History
/conversations/:id          → View Conversation Details
/services                   → Services Management
/services/new               → Add Service
/services/:id               → Edit Service
/whatsapp                   → WhatsApp Integration Status
/settings                   → Business Settings
/settings/team              → Team Members
/settings/business          → Business Profile
/settings/ai                → AI Configuration
/login                      → Login Page
```

---

## 📂 Frontend Folder Structure

```
src/
├── api/                    # API Service Layer
│   ├── auth.ts            # Authentication APIs
│   ├── appointments.ts    # Appointment APIs
│   ├── conversations.ts   # Conversation APIs
│   ├── services.ts        # Service APIs
│   ├── ai.ts              # AI Chat APIs (if direct endpoint exists)
│   └── business.ts        # Business settings APIs
│
├── components/
│   ├── dashboard/         # Dashboard-specific components
│   │   ├── StatCard.tsx
│   │   ├── AppointmentCalendar.tsx
│   │   ├── ConversationList.tsx
│   │   └── ServiceCard.tsx
│   │
│   ├── ai/                # AI Receptionist components
│   │   ├── ChatWindow.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── AISettings.tsx
│   │   └── ConversationHistory.tsx
│   │
│   ├── appointments/      # Appointment components
│   │   ├── AppointmentForm.tsx
│   │   ├── AppointmentCard.tsx
│   │   └── AppointmentFilters.tsx
│   │
│   ├── layout/            # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── ProtectedRoute.tsx
│   │
│   └── ui/                # Shadcn UI components
│
├── pages/
│   ├── Dashboard.tsx
│   ├── Login.tsx
│   ├── AIReceptionist/
│   │   ├── Index.tsx
│   │   └── Test.tsx
│   ├── Appointments/
│   │   ├── List.tsx
│   │   ├── New.tsx
│   │   └── Edit.tsx
│   ├── Conversations/
│   │   ├── List.tsx
│   │   └── Detail.tsx
│   ├── Services/
│   │   ├── List.tsx
│   │   ├── New.tsx
│   │   └── Edit.tsx
│   ├── WhatsApp.tsx
│   └── Settings/
│       ├── Index.tsx
│       ├── Business.tsx
│       ├── Team.tsx
│       └── AI.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useAppointments.ts
│   ├── useConversations.ts
│   └── useServices.ts
│
├── lib/
│   ├── api.ts             # Axios instance
│   ├── utils.ts
│   └── types.ts           # TypeScript types
│
└── App.tsx
```

---

## 🔌 API Service Layer Implementation

Each API service file should export functions that wrap the API calls:

### Example: `api/appointments.ts`
```typescript
import api from '@/lib/api';
import type { AppointmentCreate, AppointmentUpdate, AppointmentResponse } from '@/lib/types';

export const appointmentsApi = {
  list: (params?: {
    status?: string;
    date_from?: string;
    date_to?: string;
    client_phone?: string;
    skip?: number;
    limit?: number;
  }) => api.get<AppointmentResponse[]>('/appointments', { params }),
  
  get: (id: string) => api.get<AppointmentResponse>(`/appointments/${id}`),
  
  create: (data: AppointmentCreate) => api.post<AppointmentResponse>('/appointments', data),
  
  update: (id: string, data: AppointmentUpdate) => 
    api.put<AppointmentResponse>(`/appointments/${id}`, data),
  
  delete: (id: string) => api.delete(`/appointments/${id}`),
};
```

---

## 🎨 Dashboard Section Mapping

### 1. **Dashboard Overview** (`/`)
- **API Calls:**
  - `GET /appointments` → Total & upcoming appointments
  - `GET /conversations` → Total conversations
  - `GET /services` → Active services count
- **Components:**
  - StatCard (appointments, conversations, services)
  - Recent appointments list
  - AI status indicator
  - Quick action buttons

### 2. **AI Receptionist** (`/ai-receptionist`)
- **API Calls:**
  - `GET /conversations` → Conversation history
  - `GET /webhook/status` → AI agent status
- **Features:**
  - Live chat tester (sends test messages)
  - Conversation history viewer
  - AI settings (greeting, tone, instructions)
  - Model configuration

### 3. **Appointments** (`/appointments`)
- **API Calls:**
  - `GET /appointments` → List with filters
  - `POST /appointments` → Create new
  - `PUT /appointments/:id` → Update
  - `DELETE /appointments/:id` → Cancel
- **Features:**
  - Calendar view (week/month)
  - Table view with filters
  - Create/edit appointment modal
  - Status badges (confirmed, cancelled, completed)
  - Drag-and-drop scheduling

### 4. **Conversations** (`/conversations`)
- **API Calls:**
  - `GET /conversations` → List all
  - `GET /conversations/:id` → Get details
- **Features:**
  - Conversation list with search
  - Message thread viewer
  - Intent classification display
  - Collected info display

### 5. **Services** (`/services`)
- **API Calls:**
  - `GET /services` → List all
  - `POST /services` → Create new
  - `PUT /services/:id` → Update
  - `DELETE /services/:id` → Deactivate
- **Features:**
  - Service cards grid
  - Create/edit service form
  - Active/inactive toggle
  - Price & duration management

### 6. **WhatsApp Integration** (`/whatsapp`)
- **API Calls:**
  - `GET /webhook/status` → Check webhook status
- **Features:**
  - Twilio connection status
  - Webhook URL display
  - Test message sender
  - Phone number configuration

### 7. **Settings** (`/settings`)
- **Subsections:**
  - **Business Profile:** Name, hours, contact info
  - **Team Members:** User management (CRUD users)
  - **AI Configuration:** Prompts, model selection
- **API Calls:**
  - `GET /users` → List team
  - `POST /users/register` → Add user
  - Business settings (config file updates)

---

## ✅ Next Steps

1. **Create API service files** in `src/api/`
2. **Create TypeScript types** in `src/lib/types.ts`
3. **Build page components** in `src/pages/`
4. **Wire buttons & forms** to API calls
5. **Add loading & error states** using React Query
6. **Test end-to-end** integration

---

**Generated:** November 14, 2025  
**Backend Version:** FastAPI + MongoDB + Twilio + Groq  
**Frontend Version:** React + TypeScript + Shadcn UI
