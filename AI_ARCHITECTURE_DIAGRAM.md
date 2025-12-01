# AI Brain Tenant Isolation Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Dashboard → Settings → API Keys                            │   │
│  │  /dashboard/settings/api-keys/page.tsx                      │   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  [Add API Key Form]                                         │   │
│  │  Provider: [Groq ▼]   Key: [gsk_***]   [Add]              │   │
│  │                                                              │   │
│  │  [Configured Keys List]                                     │   │
│  │  • Groq: gsk_abc...xyz  [Delete]                           │   │
│  │  • VAPI: vapi_123...789 [Delete]                           │   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓ POST /api/v1/keys                      │
└─────────────────────────────────────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  /routers/webhook.py                                        │   │
│  │  POST /api/v1/webhook/whatsapp                             │   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  1. Extract phone_number_id from WhatsApp                   │   │
│  │  2. Lookup tenant: tenants.find_one({phone_number_id})    │   │
│  │  3. ❌ If not found: return 400 error                      │   │
│  │  4. ✅ If found: extract tenant_id                         │   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓ tenant_id                              │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  /ai/conversation_manager.py                                │   │
│  │  async def process_message(tenant_id, phone, message)       │   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  1. Get/Create conversation (with tenant_id)                │   │
│  │  2. Classify intent → _classify_intent(msg, history, tid)   │   │
│  │  3. Generate response → _generate_response(intent, msg, conv)│   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  _classify_intent(message, history, tenant_id)              │   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  config = db.business_config.find_one({tenant_id})         │   │
│  │  groq_api_key = security.decrypt(config.groq_api_key)      │   │
│  │  model = config.ai_config.model                            │   │
│  │  groq_agent.classify_intent(msg, api_key=key, model=model) │   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  _generate_response(intent, message, conversation)          │   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  tenant_id = conversation.tenant_id                         │   │
│  │  config = db.business_config.find_one({tenant_id})         │   │
│  │  api_key = security.decrypt(config.groq_api_key)           │   │
│  │  model = config.ai_config.model                            │   │
│  │  temperature = config.ai_config.temperature                │   │
│  │  system_prompt = config.ai_config.system_prompt            │   │
│  │  groq_agent.generate_response(                             │   │
│  │    messages, api_key, model, system_prompt, temperature)    │   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  /ai/groq_agent.py                                          │   │
│  │  async def generate_response(messages, api_key, model, ...)│   │
│  ├──────────────────────────────────────────────────────────── │   │
│  │  client = Groq(api_key=api_key)  # Per-request client!     │   │
│  │  response = await client.chat.completions.create(          │   │
│  │    model=model,                                             │   │
│  │    messages=messages,                                       │   │
│  │    temperature=temperature                                  │   │
│  │  )                                                          │   │
│  └──────────────────────────────────────────────────────────── ┘   │
│                           ↓                                         │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    GROQ API (External Service)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Tenant A requests → gsk_abc...xyz → Rate Limit A → Billing A      │
│  Tenant B requests → gsk_def...uvw → Rate Limit B → Billing B      │
│  Tenant C requests → gsk_ghi...rst → Rate Limit C → Billing C      │
│                                                                     │
│  ✅ Complete isolation per tenant's API key                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────────┐
│  MongoDB - business_config Collection                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Document for Tenant A:                                             │
│  {                                                                  │
│    "tenant_id": "tenant_a_123",                                     │
│    "groq_api_key": "AES_ENCRYPTED(gsk_abc...xyz)",                 │
│    "ai_config": {                                                   │
│      "model": "mixtral-8x7b-32768",                                 │
│      "temperature": 0.7,                                            │
│      "max_tokens": 1024,                                            │
│      "system_prompt": "You are a professional barber shop..."      │
│    }                                                                │
│  }                                                                  │
│                                                                     │
│  Document for Tenant B:                                             │
│  {                                                                  │
│    "tenant_id": "tenant_b_456",                                     │
│    "groq_api_key": "AES_ENCRYPTED(gsk_def...uvw)",                 │
│    "ai_config": {                                                   │
│      "model": "llama3-70b-8192",                                    │
│      "temperature": 0.5,                                            │
│      "max_tokens": 512,                                             │
│      "system_prompt": "You are a friendly dental clinic..."        │
│    }                                                                │
│  }                                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow Timeline

```
Time  │ Component               │ Action
──────┼─────────────────────────┼──────────────────────────────────────
T0    │ WhatsApp Cloud          │ User sends message "Book appointment"
T1    │ Webhook Handler         │ Receives POST /webhook/whatsapp
T2    │ Webhook Handler         │ Extracts phone_number_id: "12345"
T3    │ Webhook Handler         │ DB Query: tenants.find_one({phone_number_id})
T4    │ MongoDB                 │ Returns tenant document
T5    │ Webhook Handler         │ Extracts tenant_id: "tenant_a_123"
T6    │ ConversationManager     │ process_message(tenant_a_123, phone, msg)
T7    │ ConversationManager     │ _classify_intent(..., tenant_a_123)
T8    │ MongoDB                 │ Load business_config for tenant_a_123
T9    │ Security Utils          │ Decrypt groq_api_key
T10   │ GroqAgent               │ classify_intent(msg, api_key=decrypted_key)
T11   │ Groq API                │ POST to Groq with tenant_a's key
T12   │ Groq API                │ Returns intent: "book_appointment"
T13   │ ConversationManager     │ _generate_response(intent, msg, conv)
T14   │ MongoDB                 │ Load business_config for tenant_a_123
T15   │ Security Utils          │ Decrypt groq_api_key
T16   │ GroqAgent               │ generate_response(..., api_key, model, prompt)
T17   │ Groq API                │ POST to Groq with tenant_a's key
T18   │ Groq API                │ Returns AI response text
T19   │ WhatsApp Cloud          │ Send response to user
```

## Isolation Guarantees

### ✅ What is Isolated:

```
┌──────────────────┬────────────────┬────────────────────────────────┐
│ Isolation Layer  │ Mechanism      │ Benefit                        │
├──────────────────┼────────────────┼────────────────────────────────┤
│ API Keys         │ Per-tenant DB  │ Cost attribution, security     │
│ Rate Limits      │ Groq per-key   │ No shared throttling           │
│ AI Models        │ Config per TID │ Performance tuning per tenant  │
│ System Prompts   │ Config per TID │ Brand voice customization      │
│ Conversations    │ TID in DB      │ Data privacy                   │
│ Webhook Messages │ Phone→Tenant   │ Message routing isolation      │
│ Client Objects   │ Per-request    │ No shared state/memory         │
└──────────────────┴────────────────┴────────────────────────────────┘
```

### ❌ What is NOT Shared:

- ❌ Groq API client objects (new per request)
- ❌ API keys (encrypted per tenant)
- ❌ Rate limits (Groq enforces per key)
- ❌ Conversation history (tenant_id filtered)
- ❌ System prompts (tenant-specific)
- ❌ AI configuration (tenant-specific)

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Frontend Access Control                           │
│  - JWT authentication required                              │
│  - Endpoints filter by current_user.tenant_id               │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: API Key Encryption                                │
│  - Keys encrypted with AES at rest                          │
│  - Decrypted only when needed for API calls                 │
│  - Never logged or sent to frontend                         │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Tenant Resolution                                 │
│  - Webhook validates tenant exists                          │
│  - Returns 400 if not found (no fallback)                   │
│  - All DB queries filtered by tenant_id                     │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Per-Request Isolation                             │
│  - New Groq client created per request                      │
│  - Tenant config loaded fresh each time                     │
│  - No shared state or caching between tenants               │
└─────────────────────────────────────────────────────────────┘
```

## Code Flow Examples

### Example 1: Tenant A sends message

```python
# Webhook receives message
phone_number_id = "12345"  # Tenant A's WhatsApp number
tenant = db.tenants.find_one({"phone_number_id": phone_number_id})
tenant_id = tenant["tenant_id"]  # "tenant_a_123"

# Conversation manager processes
config = db.business_config.find_one({"tenant_id": "tenant_a_123"})
api_key = security.decrypt(config["groq_api_key"])  # gsk_abc...xyz

# Groq agent creates new client
client = Groq(api_key="gsk_abc...xyz")  # Tenant A's key
response = await client.chat.completions.create(...)
```

### Example 2: Tenant B sends message (simultaneously)

```python
# Different webhook request (parallel)
phone_number_id = "67890"  # Tenant B's WhatsApp number
tenant = db.tenants.find_one({"phone_number_id": phone_number_id})
tenant_id = tenant["tenant_id"]  # "tenant_b_456"

# Separate conversation manager instance
config = db.business_config.find_one({"tenant_id": "tenant_b_456"})
api_key = security.decrypt(config["groq_api_key"])  # gsk_def...uvw

# Separate Groq client
client = Groq(api_key="gsk_def...uvw")  # Tenant B's key
response = await client.chat.completions.create(...)
```

**Result:** Both tenants processed simultaneously with complete isolation!

---

**Architecture Status:** ✅ Complete  
**Isolation Level:** Full multi-tenant  
**Ready for:** Production deployment
