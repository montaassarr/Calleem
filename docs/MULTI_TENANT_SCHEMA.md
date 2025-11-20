# Multi-Tenant Database Schema & Data Architecture

> **MongoDB Collections, Indexes, and Data Partitioning for Multi-Client SaaS**  
> Last Updated: November 20, 2025

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Collections](#core-collections)
3. [Sharding Strategy](#sharding-strategy)
4. [Indexes](#indexes)
5. [Data Relationships](#data-relationships)
6. [Sample Queries](#sample-queries)
7. [DynamoDB Tables](#dynamodb-tables)
8. [Redis Cache Strategy](#redis-cache-strategy)

---

## Schema Overview

### Database Structure

```
ai_receptionist (MongoDB Database)
├── clients                    # Tenant/business accounts
├── users                      # Admin users per client
├── voice_calls                # Call logs & transcripts
├── whatsapp_messages          # WhatsApp conversations
├── appointments               # Scheduled appointments
├── services                   # Service catalog per client
├── business_configs           # Client settings & AI prompts
├── subscriptions              # Stripe subscription records
├── usage_metrics              # Metering data for billing
├── phone_numbers              # Client-owned or virtual numbers
├── api_keys                   # Third-party API credentials
└── audit_logs                 # System activity tracking
```

---

## Core Collections

### 1. `clients` Collection

**Purpose:** Store tenant/business information

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  client_id: "client_abc123",              // Unique client identifier
  created_at: ISODate("2025-01-15T10:00:00Z"),
  updated_at: ISODate("2025-11-20T14:30:00Z"),
  
  // Business Information
  business_name: "Royal Fade Barbershop",
  business_type: "barbershop",            // barbershop, salon, spa, clinic, restaurant
  email: "info@royalfade.com",
  phone: "+15551234567",
  website: "https://royalfade.com",
  
  // Address
  address: {
    street: "123 Main Street",
    city: "New York",
    state: "NY",
    postal_code: "10001",
    country: "US"
  },
  
  // Multi-Language Settings
  languages: ["en", "es", "fr"],
  default_language: "en",
  timezone: "America/New_York",
  currency: "USD",
  
  // Branding (White-Label)
  branding: {
    logo_url: "https://cdn.yourdomain.com/clients/abc123/logo.png",
    primary_color: "#1a73e8",
    secondary_color: "#34a853",
    custom_domain: "booking.royalfade.com",    // Custom subdomain
    favicon_url: "https://cdn.yourdomain.com/clients/abc123/favicon.ico"
  },
  
  // Subscription Status
  subscription: {
    plan: "pro",                           // starter, pro, enterprise
    status: "active",                      // active, past_due, cancelled, trialing
    stripe_customer_id: "cus_abc123",
    stripe_subscription_id: "sub_def456",
    current_period_start: ISODate("2025-11-01T00:00:00Z"),
    current_period_end: ISODate("2025-12-01T00:00:00Z"),
    trial_end: null,
    cancel_at: null
  },
  
  // Usage Limits (Plan-Based)
  limits: {
    max_phone_numbers: 3,
    max_users: 5,
    max_call_minutes_per_month: 1000,
    max_whatsapp_messages_per_month: 5000,
    max_ai_voices: 10
  },
  
  // Current Usage (Reset Monthly)
  usage: {
    call_minutes_used: 450,
    whatsapp_messages_used: 1200,
    phone_numbers_active: 2,
    users_active: 3,
    last_reset: ISODate("2025-11-01T00:00:00Z")
  },
  
  // Settings
  settings: {
    business_hours: {
      monday: { open: "09:00", close: "18:00", closed: false },
      tuesday: { open: "09:00", close: "18:00", closed: false },
      wednesday: { open: "09:00", close: "18:00", closed: false },
      thursday: { open: "09:00", close: "18:00", closed: false },
      friday: { open: "09:00", close: "18:00", closed: false },
      saturday: { open: "10:00", close: "16:00", closed: false },
      sunday: { open: null, close: null, closed: true }
    },
    appointment_duration_default: 30,      // minutes
    booking_advance_days: 30,              // How far ahead clients can book
    cancellation_policy_hours: 24,
    send_confirmation_sms: true,
    send_reminder_24h: true,
    send_reminder_2h: true
  },
  
  // Status
  status: "active",                        // active, suspended, cancelled
  onboarding_completed: true,
  onboarding_step: null,                   // null if completed, or step number
  
  // Metadata
  tags: ["premium", "verified"],
  notes: "VIP client, priority support",
  referral_source: "google_ads"
}
```

**Indexes:**
```javascript
db.clients.createIndex({ client_id: 1 }, { unique: true })
db.clients.createIndex({ "subscription.status": 1 })
db.clients.createIndex({ status: 1 })
db.clients.createIndex({ created_at: -1 })
```

---

### 2. `users` Collection

**Purpose:** Store admin/staff users for each client

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439012"),
  user_id: "user_xyz789",
  client_id: "client_abc123",              // Foreign key to clients
  created_at: ISODate("2025-01-15T10:05:00Z"),
  updated_at: ISODate("2025-11-20T14:35:00Z"),
  
  // Authentication
  email: "admin@royalfade.com",
  username: "admin",
  password_hash: "$2b$12$abcdef...",       // Argon2 or bcrypt
  email_verified: true,
  phone: "+15551234567",
  phone_verified: false,
  
  // Profile
  first_name: "John",
  last_name: "Smith",
  display_name: "John Smith",
  avatar_url: "https://cdn.yourdomain.com/avatars/xyz789.jpg",
  
  // Role & Permissions
  role: "admin",                           // admin, manager, viewer
  permissions: [
    "read:calls",
    "write:calls",
    "read:appointments",
    "write:appointments",
    "read:config",
    "write:config",
    "read:billing",
    "write:billing"
  ],
  
  // Settings
  language: "en",
  timezone: "America/New_York",
  notifications: {
    email_new_appointment: true,
    email_missed_call: true,
    sms_urgent_alerts: false,
    dashboard_sounds: true
  },
  
  // Session Management
  last_login: ISODate("2025-11-20T14:35:00Z"),
  last_ip: "192.168.1.100",
  failed_login_attempts: 0,
  locked_until: null,
  
  // Status
  status: "active",                        // active, inactive, suspended
  invited_by: "user_abc000",
  accepted_invite: true
}
```

**Indexes:**
```javascript
db.users.createIndex({ user_id: 1 }, { unique: true })
db.users.createIndex({ client_id: 1, email: 1 }, { unique: true })
db.users.createIndex({ client_id: 1, status: 1 })
db.users.createIndex({ email: 1 })
```

---

### 3. `voice_calls` Collection

**Purpose:** Store call logs, transcripts, recordings

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439013"),
  call_id: "call_vapi_abc123",
  client_id: "client_abc123",              // CRITICAL: Tenant isolation
  created_at: ISODate("2025-11-20T15:00:00Z"),
  updated_at: ISODate("2025-11-20T15:12:00Z"),
  
  // Call Metadata
  direction: "inbound",                    // inbound, outbound
  status: "completed",                     // initiated, ringing, in_progress, completed, failed, no_answer
  duration_seconds: 720,
  
  // Participants
  from_number: "+15559876543",
  to_number: "+15551234567",               // Client's business number
  voice_contact_id: "voice_call_abc123",   // Synthetic ID for WebRTC
  customer_name: "Jane Doe",               // Extracted from conversation
  
  // Vapi Integration
  vapi_call_id: "vapi_abc123def456",
  vapi_assistant_id: "asst_xyz789",
  
  // AI Voice Configuration (Snapshot)
  voice_config: {
    model_provider: "groq",
    model_name: "llama-3.3-70b-versatile",
    temperature: 0.7,
    voice_provider: "11labs",
    voice_id: "rachel",
    language: "en"
  },
  
  // Conversation Transcript
  transcript: [
    {
      timestamp: ISODate("2025-11-20T15:00:05Z"),
      role: "assistant",
      message: "Hello, this is Ava from Royal Fade. How can I help you today?",
      audio_duration: 3.5
    },
    {
      timestamp: ISODate("2025-11-20T15:00:10Z"),
      role: "user",
      message: "Hi, I'd like to book a haircut for tomorrow at 2 PM.",
      audio_duration: 2.8
    },
    {
      timestamp: ISODate("2025-11-20T15:00:15Z"),
      role: "assistant",
      message: "Sure! Let me check our availability for tomorrow at 2 PM.",
      audio_duration: 3.2
    }
    // ... more turns
  ],
  
  // Tool Calls (Actions Taken)
  tool_calls: [
    {
      tool_name: "check_availability",
      arguments: {
        date: "2025-11-21",
        time: "14:00",
        service: "Haircut"
      },
      result: {
        available: true,
        slots: ["14:00", "14:30", "15:00"]
      },
      executed_at: ISODate("2025-11-20T15:00:16Z")
    },
    {
      tool_name: "book_appointment",
      arguments: {
        customer_name: "Jane Doe",
        customer_phone: "+15559876543",
        service_name: "Haircut",
        scheduled_time: "2025-11-21T14:00:00Z",
        duration_minutes: 30
      },
      result: {
        success: true,
        appointment_id: "apt_abc123"
      },
      executed_at: ISODate("2025-11-20T15:00:20Z")
    }
  ],
  
  // Recording
  recording_url: "s3://ai-receptionist-recordings/clients/abc123/calls/vapi_abc123.mp3",
  recording_duration: 720,
  recording_size_bytes: 5760000,
  
  // Analytics
  sentiment: "positive",                   // positive, neutral, negative (AI-detected)
  intent: "booking",                       // booking, inquiry, complaint, general
  outcome: "appointment_booked",           // appointment_booked, info_provided, escalated, no_action
  customer_satisfaction: 4.5,              // 1-5 rating (if collected)
  
  // Cost Tracking
  cost: {
    voice_minutes: 12,                     // Duration in minutes
    voice_cost_usd: 0.84,                  // 12 * $0.07
    llm_tokens: 1500,
    llm_cost_usd: 0.0004,                  // 1500 * $0.27/1M
    tts_characters: 850,
    tts_cost_usd: 0.26,                    // 850 * $0.30/1K
    total_cost_usd: 1.10
  },
  
  // Metadata
  tags: ["booking_success", "new_customer"],
  notes: "Customer mentioned referral from Google",
  flagged: false,
  flagged_reason: null
}
```

**Indexes:**
```javascript
db.voice_calls.createIndex({ call_id: 1 }, { unique: true })
db.voice_calls.createIndex({ client_id: 1, created_at: -1 })
db.voice_calls.createIndex({ client_id: 1, status: 1 })
db.voice_calls.createIndex({ client_id: 1, from_number: 1, created_at: -1 })
db.voice_calls.createIndex({ client_id: 1, outcome: 1 })
db.voice_calls.createIndex({ vapi_call_id: 1 })
```

---

### 4. `whatsapp_messages` Collection

**Purpose:** Store WhatsApp conversations

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439014"),
  message_id: "wamid.abc123def456",        // WhatsApp message ID
  client_id: "client_abc123",
  created_at: ISODate("2025-11-20T16:00:00Z"),
  
  // Conversation Context
  conversation_id: "conv_xyz789",          // Groups messages in thread
  contact_id: "+15559876543",              // Customer's WhatsApp number
  contact_name: "Jane Doe",
  
  // Message Details
  direction: "inbound",                    // inbound, outbound
  type: "text",                            // text, image, audio, video, document
  content: {
    text: "Hi, can I book a haircut for tomorrow?",
    media_url: null,
    media_mime_type: null,
    caption: null
  },
  
  // Meta Cloud API Data
  from: "+15559876543",
  to: "123456789",                         // Business WhatsApp number ID
  timestamp: ISODate("2025-11-20T16:00:00Z"),
  status: "delivered",                     // sent, delivered, read, failed
  
  // AI Processing
  intent: "booking",
  entities: {
    service: "Haircut",
    date: "2025-11-21",
    time: "14:00"
  },
  sentiment: "neutral",
  
  // Response (if outbound)
  response_to: "wamid.xyz789abc123",       // Original message ID
  auto_response: true,                     // AI-generated or manual
  
  // Cost
  cost_usd: 0.005,                         // WhatsApp Business API pricing
  
  // Metadata
  tags: ["booking_inquiry"],
  flagged: false
}
```

**Indexes:**
```javascript
db.whatsapp_messages.createIndex({ message_id: 1 }, { unique: true })
db.whatsapp_messages.createIndex({ client_id: 1, created_at: -1 })
db.whatsapp_messages.createIndex({ client_id: 1, conversation_id: 1, created_at: 1 })
db.whatsapp_messages.createIndex({ client_id: 1, contact_id: 1, created_at: -1 })
```

---

### 5. `appointments` Collection

**Purpose:** Store scheduled appointments

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439015"),
  appointment_id: "apt_abc123",
  client_id: "client_abc123",
  created_at: ISODate("2025-11-20T15:00:25Z"),
  updated_at: ISODate("2025-11-20T15:00:25Z"),
  
  // Customer Information
  customer_name: "Jane Doe",
  customer_phone: "+15559876543",
  customer_email: "jane@example.com",
  contact_id: "+15559876543",              // Links to conversations
  
  // Appointment Details
  service_id: "svc_haircut_001",
  service_name: "Haircut",
  scheduled_time: ISODate("2025-11-21T14:00:00Z"),
  duration_minutes: 30,
  end_time: ISODate("2025-11-21T14:30:00Z"),
  
  // Status
  status: "confirmed",                     // pending, confirmed, completed, cancelled, no_show
  confirmation_sent: true,
  confirmation_sent_at: ISODate("2025-11-20T15:00:30Z"),
  reminder_sent_24h: false,
  reminder_sent_2h: false,
  
  // Source
  booked_via: "voice_call",                // voice_call, whatsapp, dashboard, api
  booked_by: "call_vapi_abc123",           // Call ID or user ID
  
  // Cancellation
  cancelled_at: null,
  cancelled_by: null,
  cancellation_reason: null,
  
  // Notes
  notes: "Customer requested senior stylist",
  internal_notes: "VIP client",
  
  // Pricing
  price: 35.00,
  currency: "USD",
  paid: false,
  payment_method: null,
  
  // Metadata
  tags: ["new_customer"],
  flagged: false
}
```

**Indexes:**
```javascript
db.appointments.createIndex({ appointment_id: 1 }, { unique: true })
db.appointments.createIndex({ client_id: 1, scheduled_time: 1 })
db.appointments.createIndex({ client_id: 1, status: 1, scheduled_time: 1 })
db.appointments.createIndex({ client_id: 1, customer_phone: 1 })
db.appointments.createIndex({ client_id: 1, contact_id: 1 })
```

---

### 6. `services` Collection

**Purpose:** Service catalog per client

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439016"),
  service_id: "svc_haircut_001",
  client_id: "client_abc123",
  created_at: ISODate("2025-01-15T10:10:00Z"),
  updated_at: ISODate("2025-11-20T16:05:00Z"),
  
  // Service Details
  name: "Haircut",
  description: "Professional men's haircut with style consultation",
  category: "Hair Services",
  
  // Multi-Language
  name_i18n: {
    en: "Haircut",
    es: "Corte de Cabello",
    fr: "Coupe de Cheveux"
  },
  description_i18n: {
    en: "Professional men's haircut with style consultation",
    es: "Corte de cabello profesional para hombres con consulta de estilo",
    fr: "Coupe de cheveux professionnelle pour hommes avec consultation de style"
  },
  
  // Pricing
  price: 35.00,
  currency: "USD",
  duration_minutes: 30,
  
  // Availability
  available: true,
  bookable_online: true,
  
  // Staff
  assigned_staff: ["staff_john", "staff_mike"],
  
  // Metadata
  image_url: "https://cdn.yourdomain.com/services/haircut.jpg",
  sort_order: 1,
  tags: ["popular", "men"]
}
```

**Indexes:**
```javascript
db.services.createIndex({ service_id: 1 }, { unique: true })
db.services.createIndex({ client_id: 1, available: 1 })
db.services.createIndex({ client_id: 1, sort_order: 1 })
```

---

### 7. `business_configs` Collection

**Purpose:** AI voice prompts, tool settings, configurations

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439017"),
  client_id: "client_abc123",              // One config per client
  updated_at: ISODate("2025-11-20T16:10:00Z"),
  
  // Voice Configuration
  voice_config: {
    model_provider: "groq",
    model_name: "llama-3.3-70b-versatile",
    temperature: 0.7,
    max_tokens: 512,
    
    voice_provider: "11labs",
    voice_id: "rachel",
    voice_stability: 0.5,
    voice_similarity_boost: 0.75,
    
    first_message: {
      en: "Hello, this is Ava from Royal Fade. How can I help you today?",
      es: "Hola, soy Ava de Royal Fade. ¿En qué puedo ayudarte hoy?",
      fr: "Bonjour, c'est Ava de Royal Fade. Comment puis-je vous aider aujourd'hui?"
    },
    
    system_prompt: {
      en: "You are Ava, a friendly receptionist at Royal Fade Barbershop...",
      es: "Eres Ava, una recepcionista amigable en Royal Fade Barbershop...",
      fr: "Vous êtes Ava, une réceptionniste sympathique chez Royal Fade Barbershop..."
    },
    
    enabled_tools: [
      "check_availability",
      "book_appointment",
      "reschedule_appointment",
      "cancel_appointment",
      "get_services"
    ],
    
    end_call_on_goodbye: true,
    record_calls: true,
    silence_timeout_seconds: 30,
    max_call_duration_seconds: 600
  },
  
  // WhatsApp Configuration
  whatsapp_config: {
    auto_reply_enabled: true,
    business_hours_only: true,
    greeting_message: {
      en: "Hi! Thanks for messaging Royal Fade. How can we help you?",
      es: "¡Hola! Gracias por contactar a Royal Fade. ¿Cómo podemos ayudarte?",
      fr: "Salut! Merci de contacter Royal Fade. Comment pouvons-nous vous aider?"
    },
    away_message: {
      en: "We're currently closed. Our hours are Monday-Saturday 9 AM - 6 PM.",
      es: "Actualmente estamos cerrados. Nuestro horario es de lunes a sábado de 9 AM a 6 PM.",
      fr: "Nous sommes actuellement fermés. Nos heures sont du lundi au samedi de 9h à 18h."
    }
  },
  
  // Notification Settings
  notification_config: {
    admin_email: "admin@royalfade.com",
    notify_new_appointment: true,
    notify_cancellation: true,
    notify_missed_call: true,
    notify_whatsapp_message: false
  }
}
```

**Indexes:**
```javascript
db.business_configs.createIndex({ client_id: 1 }, { unique: true })
```

---

### 8. `subscriptions` Collection

**Purpose:** Stripe subscription tracking

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439018"),
  subscription_id: "sub_def456",
  client_id: "client_abc123",
  created_at: ISODate("2025-01-15T10:00:00Z"),
  updated_at: ISODate("2025-11-01T00:00:00Z"),
  
  // Stripe Data
  stripe_customer_id: "cus_abc123",
  stripe_subscription_id: "sub_def456",
  stripe_price_id: "price_pro_monthly",
  
  // Plan Details
  plan: "pro",                             // starter, pro, enterprise
  billing_cycle: "monthly",                // monthly, annual
  amount: 99.00,
  currency: "USD",
  
  // Period
  current_period_start: ISODate("2025-11-01T00:00:00Z"),
  current_period_end: ISODate("2025-12-01T00:00:00Z"),
  
  // Status
  status: "active",                        // active, past_due, cancelled, trialing, incomplete
  cancel_at_period_end: false,
  cancelled_at: null,
  
  // Trial
  trial_start: ISODate("2025-01-15T10:00:00Z"),
  trial_end: ISODate("2025-01-29T10:00:00Z"),
  
  // Add-Ons
  add_ons: [
    {
      name: "extra_phone_number",
      quantity: 2,
      price_per_unit: 10.00,
      total: 20.00
    }
  ],
  
  // Payment Method
  payment_method: {
    type: "card",
    last4: "4242",
    brand: "visa",
    exp_month: 12,
    exp_year: 2026
  }
}
```

**Indexes:**
```javascript
db.subscriptions.createIndex({ subscription_id: 1 }, { unique: true })
db.subscriptions.createIndex({ client_id: 1 })
db.subscriptions.createIndex({ stripe_subscription_id: 1 }, { unique: true })
db.subscriptions.createIndex({ status: 1 })
```

---

### 9. `usage_metrics` Collection

**Purpose:** Track usage for billing (metered)

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439019"),
  client_id: "client_abc123",
  date: ISODate("2025-11-20T00:00:00Z"),   // Daily aggregation
  
  // Voice Calls
  call_count: 45,
  call_minutes: 450,
  call_cost_usd: 31.50,
  
  // WhatsApp
  whatsapp_message_count: 120,
  whatsapp_cost_usd: 0.60,
  
  // LLM
  llm_tokens: 50000,
  llm_cost_usd: 0.0135,
  
  // TTS
  tts_characters: 25000,
  tts_cost_usd: 7.50,
  
  // Total
  total_cost_usd: 39.61,
  
  // Reported to Stripe
  reported_to_stripe: true,
  stripe_usage_record_id: "mbur_abc123"
}
```

**Indexes:**
```javascript
db.usage_metrics.createIndex({ client_id: 1, date: -1 })
db.usage_metrics.createIndex({ date: -1 })
```

---

### 10. `phone_numbers` Collection

**Purpose:** Track client phone numbers (Twilio virtual or forwarded)

```javascript
{
  _id: ObjectId("507f1f77bcf86cd79943901a"),
  phone_number_id: "pn_abc123",
  client_id: "client_abc123",
  created_at: ISODate("2025-01-15T10:15:00Z"),
  
  // Number Details
  phone_number: "+15551234567",
  country_code: "US",
  number_type: "virtual",                  // virtual (Twilio), forwarded (client-owned)
  
  // Provider (if virtual)
  provider: "twilio",
  provider_sid: "PN1234567890abcdef",
  
  // Forwarding (if client-owned)
  forward_to: null,                        // Client's actual number
  forward_enabled: false,
  
  // Capabilities
  voice_enabled: true,
  sms_enabled: true,
  
  // Status
  status: "active",                        // active, suspended, released
  
  // Cost
  monthly_cost_usd: 1.00,                  // Twilio phone number rental
  
  // Usage
  calls_inbound: 150,
  calls_outbound: 5,
  sms_inbound: 30,
  sms_outbound: 10
}
```

**Indexes:**
```javascript
db.phone_numbers.createIndex({ phone_number_id: 1 }, { unique: true })
db.phone_numbers.createIndex({ client_id: 1 })
db.phone_numbers.createIndex({ phone_number: 1 }, { unique: true })
db.phone_numbers.createIndex({ status: 1 })
```

---

### 11. `api_keys` Collection

**Purpose:** Third-party API credentials per client

```javascript
{
  _id: ObjectId("507f1f77bcf86cd79943901b"),
  api_key_id: "ak_abc123",
  client_id: "client_abc123",
  created_at: ISODate("2025-01-15T10:20:00Z"),
  
  // Key Details
  key: "REDACTED_STRIPE_KEY",             // Hashed in production
  key_prefix: "sk_live_",
  name: "Production API Key",
  
  // Permissions
  permissions: ["read:calls", "write:appointments"],
  
  // Rate Limits
  rate_limit_per_minute: 100,
  rate_limit_per_day: 10000,
  
  // Usage
  last_used: ISODate("2025-11-20T16:15:00Z"),
  usage_count: 5000,
  
  // Status
  status: "active",                        // active, revoked
  expires_at: null
}
```

**Indexes:**
```javascript
db.api_keys.createIndex({ api_key_id: 1 }, { unique: true })
db.api_keys.createIndex({ client_id: 1 })
db.api_keys.createIndex({ key: 1 }, { unique: true })
```

---

### 12. `audit_logs` Collection

**Purpose:** Track all important system events

```javascript
{
  _id: ObjectId("507f1f77bcf86cd79943901c"),
  log_id: "log_abc123",
  client_id: "client_abc123",
  timestamp: ISODate("2025-11-20T16:20:00Z"),
  
  // Event Details
  event_type: "appointment.created",       // appointment.created, user.login, config.updated, etc.
  actor_type: "user",                      // user, system, api_key
  actor_id: "user_xyz789",
  
  // Action
  action: "create",                        // create, update, delete, read
  resource_type: "appointment",
  resource_id: "apt_abc123",
  
  // Changes (for updates)
  changes: {
    before: { status: "pending" },
    after: { status: "confirmed" }
  },
  
  // Metadata
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  metadata: {
    source: "dashboard",
    session_id: "sess_xyz123"
  }
}
```

**Indexes:**
```javascript
db.audit_logs.createIndex({ log_id: 1 }, { unique: true })
db.audit_logs.createIndex({ client_id: 1, timestamp: -1 })
db.audit_logs.createIndex({ event_type: 1, timestamp: -1 })
db.audit_logs.createIndex({ actor_id: 1, timestamp: -1 })
```

---

## Sharding Strategy

### Shard Key Selection

**Primary Shard Key:** `client_id`

**Rationale:**
- Natural tenant boundary
- Queries are always scoped to client_id
- Even distribution if client sizes are similar
- Allows for future client-specific shard allocation

**Shard Configuration:**
```javascript
// Enable sharding on database
sh.enableSharding("ai_receptionist")

// Shard collections
sh.shardCollection("ai_receptionist.clients", { client_id: 1 })
sh.shardCollection("ai_receptionist.users", { client_id: 1 })
sh.shardCollection("ai_receptionist.voice_calls", { client_id: 1, created_at: 1 })
sh.shardCollection("ai_receptionist.whatsapp_messages", { client_id: 1, created_at: 1 })
sh.shardCollection("ai_receptionist.appointments", { client_id: 1, scheduled_time: 1 })
sh.shardCollection("ai_receptionist.services", { client_id: 1 })
sh.shardCollection("ai_receptionist.business_configs", { client_id: 1 })
sh.shardCollection("ai_receptionist.subscriptions", { client_id: 1 })
sh.shardCollection("ai_receptionist.usage_metrics", { client_id: 1, date: 1 })
sh.shardCollection("ai_receptionist.phone_numbers", { client_id: 1 })
sh.shardCollection("ai_receptionist.api_keys", { client_id: 1 })
sh.shardCollection("ai_receptionist.audit_logs", { client_id: 1, timestamp: 1 })
```

---

## Indexes

### Compound Indexes for Performance

```javascript
// Voice Calls - Common Queries
db.voice_calls.createIndex({ client_id: 1, created_at: -1 })
db.voice_calls.createIndex({ client_id: 1, status: 1, created_at: -1 })
db.voice_calls.createIndex({ client_id: 1, from_number: 1, created_at: -1 })
db.voice_calls.createIndex({ client_id: 1, outcome: 1, created_at: -1 })

// Appointments - Scheduling Queries
db.appointments.createIndex({ client_id: 1, scheduled_time: 1 })
db.appointments.createIndex({ client_id: 1, status: 1, scheduled_time: 1 })
db.appointments.createIndex({ client_id: 1, customer_phone: 1, scheduled_time: -1 })

// WhatsApp Messages - Conversation Threads
db.whatsapp_messages.createIndex({ client_id: 1, conversation_id: 1, created_at: 1 })
db.whatsapp_messages.createIndex({ client_id: 1, contact_id: 1, created_at: -1 })

// Usage Metrics - Billing Queries
db.usage_metrics.createIndex({ client_id: 1, date: -1 })
db.usage_metrics.createIndex({ date: -1, reported_to_stripe: 1 })
```

---

## Data Relationships

### Entity Relationship Diagram

```
┌─────────────────┐
│    clients      │
│                 │
│ client_id (PK)  │◄─────┐
└─────────────────┘      │
                         │
         ┌───────────────┼───────────────────────────────┐
         │               │                               │
         │               │                               │
    ┌────▼─────┐  ┌──────▼──────┐  ┌──────────────┐  ┌──▼───────────┐
    │  users   │  │ voice_calls │  │ appointments │  │ subscriptions│
    │          │  │             │  │              │  │              │
    │ user_id  │  │ call_id     │  │ appointment  │  │ subscription │
    │ client_id│  │ client_id   │  │ _id          │  │ _id          │
    └──────────┘  │ contact_id  │  │ client_id    │  │ client_id    │
                  └─────────────┘  │ contact_id   │  └──────────────┘
                                   └──────────────┘
                         │
                         │
                  ┌──────▼──────────┐
                  │ whatsapp_       │
                  │ messages        │
                  │                 │
                  │ message_id      │
                  │ client_id       │
                  │ contact_id      │
                  └─────────────────┘
```

---

## Sample Queries

### 1. Get All Calls for a Client (Last 30 Days)

```javascript
db.voice_calls.find({
  client_id: "client_abc123",
  created_at: { 
    $gte: ISODate("2025-10-21T00:00:00Z"),
    $lte: ISODate("2025-11-20T23:59:59Z")
  }
}).sort({ created_at: -1 }).limit(100)
```

### 2. Get Appointments for Tomorrow

```javascript
db.appointments.find({
  client_id: "client_abc123",
  scheduled_time: {
    $gte: ISODate("2025-11-21T00:00:00Z"),
    $lt: ISODate("2025-11-22T00:00:00Z")
  },
  status: { $in: ["pending", "confirmed"] }
}).sort({ scheduled_time: 1 })
```

### 3. Calculate Monthly Usage

```javascript
db.voice_calls.aggregate([
  {
    $match: {
      client_id: "client_abc123",
      created_at: {
        $gte: ISODate("2025-11-01T00:00:00Z"),
        $lt: ISODate("2025-12-01T00:00:00Z")
      },
      status: "completed"
    }
  },
  {
    $group: {
      _id: null,
      total_calls: { $sum: 1 },
      total_minutes: { $sum: { $divide: ["$duration_seconds", 60] } },
      total_cost: { $sum: "$cost.total_cost_usd" }
    }
  }
])
```

### 4. Get Conversation History for Customer

```javascript
db.whatsapp_messages.find({
  client_id: "client_abc123",
  contact_id: "+15559876543"
}).sort({ created_at: 1 })
```

### 5. Check Availability (No Double-Booking)

```javascript
db.appointments.find({
  client_id: "client_abc123",
  scheduled_time: {
    $lt: ISODate("2025-11-21T14:30:00Z")  // Requested end time
  },
  end_time: {
    $gt: ISODate("2025-11-21T14:00:00Z")  // Requested start time
  },
  status: { $in: ["pending", "confirmed"] }
}).count()
// If count > 0, slot is taken
```

---

## DynamoDB Tables

### Phone Number → Client Mapping

**Table:** `phone_number_lookup`

**Purpose:** Fast lookup for incoming calls/messages

```json
{
  "phone_number": "+15551234567",     // Partition Key
  "client_id": "client_abc123",
  "number_type": "virtual",
  "provider": "twilio",
  "created_at": "2025-01-15T10:15:00Z",
  "ttl": 1735689600                   // Auto-delete after expiry
}
```

### API Key → Client Mapping

**Table:** `api_key_lookup`

```json
{
  "api_key_hash": "sha256_hash...",   // Partition Key
  "client_id": "client_abc123",
  "permissions": ["read:calls", "write:appointments"],
  "rate_limit_per_minute": 100,
  "created_at": "2025-01-15T10:20:00Z"
}
```

---

## Redis Cache Strategy

### Cache Keys

```
# Client configuration (TTL: 5 minutes)
client:{client_id}:config → JSON serialized business_configs

# User session (TTL: 30 days)
session:{session_id} → { user_id, client_id, expires_at }

# Rate limiting (TTL: 1 minute)
ratelimit:api:{api_key}:{minute} → counter

# Phone number lookup (TTL: 1 hour)
phone:{phone_number}:client_id → client_id

# Available time slots (TTL: 30 seconds)
availability:{client_id}:{date} → [timestamps]
```

### Example Usage

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache client config
def get_client_config(client_id: str) -> dict:
    cache_key = f"client:{client_id}:config"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Fetch from MongoDB
    config = db.business_configs.find_one({"client_id": client_id})
    
    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(config))
    
    return config

# Rate limiting
def check_rate_limit(api_key: str, limit: int = 100) -> bool:
    minute = datetime.now().strftime("%Y%m%d%H%M")
    key = f"ratelimit:api:{api_key}:{minute}"
    
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    
    return current <= limit
```

---

## Data Migration Scripts

### Initial Client Setup

```python
# scripts/create_client.py
from datetime import datetime, timedelta
from pymongo import MongoClient
import secrets

def create_client(business_name: str, email: str, plan: str = "starter"):
    """Create a new client with default configuration"""
    
    client_id = f"client_{secrets.token_hex(8)}"
    
    client_doc = {
        "client_id": client_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "business_name": business_name,
        "email": email,
        "subscription": {
            "plan": plan,
            "status": "trialing",
            "trial_end": datetime.utcnow() + timedelta(days=14)
        },
        "limits": {
            "max_phone_numbers": 1 if plan == "starter" else 3,
            "max_call_minutes_per_month": 500 if plan == "starter" else 1000
        },
        "status": "active",
        "onboarding_completed": False,
        "onboarding_step": 1
    }
    
    db.clients.insert_one(client_doc)
    
    # Create default admin user
    user_doc = {
        "user_id": f"user_{secrets.token_hex(8)}",
        "client_id": client_id,
        "email": email,
        "role": "admin",
        "status": "active"
    }
    db.users.insert_one(user_doc)
    
    # Create default business config
    config_doc = {
        "client_id": client_id,
        "voice_config": {
            "model_provider": "groq",
            "model_name": "llama-3.3-70b-versatile",
            "voice_provider": "11labs",
            "voice_id": "rachel"
        }
    }
    db.business_configs.insert_one(config_doc)
    
    return client_id
```

---

**Next Documents:**
- [DevOps & CI/CD](DEVOPS_CICD.md)
- [Production Deployment](PRODUCTION_DEPLOYMENT.md)
- [Client Onboarding](CLIENT_ONBOARDING.md)

---

**Document Version:** 1.0  
**Last Updated:** November 20, 2025  
**Status:** Production Ready
