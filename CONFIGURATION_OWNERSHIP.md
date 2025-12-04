# Configuration Ownership Structure

## 🏢 What Business Owners (Tenants) Control

### 1. **Business Information**
- Business name
- Phone number, email, address
- Operating hours
- Timezone
- Business logo/branding

### 2. **AI Agent Configuration**
- System prompt (personality/behavior)
- Agent name and description
- LLM model selection (from available options)
- LLM temperature
- Voice settings:
  - Voice provider (Cartesia, ElevenLabs, OpenAI)
  - Voice ID
  - Voice parameters (stability, speed)

### 3. **API Keys** (Tenant-Owned Services)
- **Groq API Key** - For LLM processing
- **Cartesia API Key** - For text-to-speech
- **ElevenLabs API Key** - Alternative TTS
- **OpenAI API Key** - Alternative LLM/TTS
- **Deepgram API Key** - For speech-to-text (optional, platform default available)

### 4. **Services & Appointments**
- Services offered (name, duration, price)
- Service descriptions
- Appointment settings
- Staff members
- Calendar configuration

### 5. **Integrations**
- N8N webhook URLs
- Custom webhook endpoints
- Google Calendar sync
- WhatsApp configuration

### 6. **Customer Data**
- Customer records
- Appointment history
- Call logs
- Analytics

---

## 🔧 What Platform (You) Control

### 1. **Infrastructure**
- **LiveKit Cloud Account** - Platform-wide
  - LiveKit URL: `wss://aireceptionist-iqt10ym2.livekit.cloud`
  - LiveKit API Key & Secret
  - Agent worker deployment
- **MongoDB Database** - Shared across all tenants
- **Backend API** - Core application logic
- **Frontend Application** - UI framework

### 2. **Platform-Level API Keys** (Optional Shared)
- **Deepgram API Key** - Default STT for all tenants (can be overridden)
- **Platform Groq/OpenAI Key** - Fallback for tenants without their own keys

### 3. **Default Settings**
- Default agent templates
- Default voice settings
- Default LLM models available
- Platform features enabled/disabled

### 4. **Security**
- Encryption keys
- JWT secrets
- Authentication system
- Authorization rules

### 5. **Multi-Tenancy Logic**
- Tenant isolation
- Data segregation
- Resource quotas
- Billing/subscription management

---

## 📊 Configuration Hierarchy

```
Platform (You)
├── LiveKit Infrastructure
│   ├── LiveKit URL (shared)
│   ├── LiveKit API credentials (shared)
│   └── Agent worker service (shared)
├── Default API Keys (optional)
│   ├── Deepgram (shared STT)
│   └── Groq/OpenAI (fallback)
└── Security & Database
    └── Encryption/Auth

Tenant (Business Owner)
├── Business Config
│   ├── Business details
│   └── Operating hours
├── Their API Keys (required)
│   ├── Groq (for their LLM)
│   ├── Cartesia (for their TTS)
│   └── Optional: ElevenLabs, OpenAI
├── AI Agent Settings
│   ├── System prompt
│   ├── Voice settings
│   └── LLM parameters
└── Business Data
    ├── Services
    ├── Appointments
    └── Customers
```

---

## 🎯 Recommended Approach

### Current Setup (Your System)
You control the **LiveKit infrastructure** and each tenant brings **their own API keys**:

```yaml
Platform:
  - LiveKit URL & credentials (shared)
  - Backend & Database
  - No shared AI API keys

Tenants:
  - Must provide: Groq + Cartesia keys
  - Configure: Agent behavior, voice, prompts
  - Manage: Their business data
```

### Alternative: Hybrid Model
You could offer **platform-level API keys** as a convenience:

```yaml
Platform:
  - LiveKit infrastructure
  - Default Groq key (all tenants share)
  - Default Cartesia key (all tenants share)
  - Default Deepgram key (all tenants share)

Tenants:
  - Can override with their own keys (optional)
  - Still configure: Agent behavior, voice
  - Manage: Their business data
```

---

## 💡 Best Practice

**For SaaS**: You (platform) should provide default API keys so tenants don't need technical setup:

1. **You control**: Infrastructure + Default API keys
2. **Tenants control**: Business config + Agent personality
3. **Advanced tenants**: Can bring their own API keys for better rates/control

This is similar to how Twilio/Stripe work - you can use platform keys or bring your own.
