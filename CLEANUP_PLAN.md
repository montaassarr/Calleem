# Backend Cleanup & Optimization Plan

## 📊 Current Analysis (December 16, 2025)

### Current Size: **319MB**

### Breakdown:
- **livekit/**: 32KB (UNUSED - to be removed)
- **ai/**: 148KB (PARTIALLY UNUSED - groq agent not used)
- **tests/**: 112KB (keeping essential tests only)
- **__pycache__/**: ~50MB+ (to be removed and gitignored)
- **Other files**: ~268MB

---

## 🎯 Cleanup Strategy

### Phase 1: Remove Unused Code & Dependencies

#### ❌ REMOVE - Not Used in E2E Flow

1. **`/livekit/`** - Entire folder (32KB)
   - Not imported in main.py
   - LiveKit integration replaced by Vapi
   - Files: `__init__.py`, `token_server.py`

2. **`/ai/`** - Partial cleanup (148KB → ~40KB)
   - ❌ Remove: `groq_agent.py` (Groq not used, Vapi handles AI)
   - ❌ Remove: `conversation_manager.py` (old chat logic, replaced by Vapi)
   - ❌ Remove: `agent.py` (empty file per user request)
   - ❌ Remove: `intents.py` (intent classification done by Vapi)
   - ❌ Remove: `prompt_templates.py` (templates in Vapi assistant)
   - ❌ Remove: `tools.py` (tools defined in Vapi)
   - ✅ Keep: `__init__.py` (if folder needed for future)

3. **Routers** - Unused/Incomplete
   - ❌ `/routers/chat.py` - Web chat not used (Vapi only)
   - ❌ `/routers/whatsapp.py` - WhatsApp not implemented
   - ❌ `/routers/billing.py` - Stripe billing not active
   - ❌ `/routers/monitoring.py` - Not actively used
   - ❌ `/routers/admin.py` - Admin analytics not fully implemented
   - ❌ `/routers/platform_keys.py` - Platform keys (Groq) not used

4. **Models** - Unused
   - ❌ `/models/agent.py` - LiveKit agent models not used
   - ❌ `/models/conversation.py` - Old conversation model (Vapi stores this)

5. **Services** - Unused
   - ❌ `/services/conversation_service.py` - Old chat service
   - ❌ `/services/email_service.py` - Email not configured
   - ❌ `/services/stripe_service.py` - Billing not active
   - ❌ `/services/mock_stripe_service.py` - Test service
   - ❌ `/services/twilio_service.py` - Using Vapi for SMS
   - ❌ `/services/admin_service.py` - Admin features not complete

6. **Utils** - Cleanup
   - ❌ `/utils/error_logger.py` - Can use standard logging
   - ❌ `/utils/text_formatter.py` - Not used

7. **Tests** - Reduce to Essential
   - ✅ Keep: `test_new_user_scenario.py`
   - ❌ Remove: `test_client_flow.py` (old flow)
   - ❌ Remove: `test_phone_integration.py` (covered by E2E)
   - ❌ Remove: `integration_health_check.py` (basic health check in main.py)

8. **Scripts**
   - ❌ `/scripts/cleanup_tenants.py` - One-time script

9. **Config Cleanup**
   - Remove LiveKit config from `utils/config.py`
   - Remove Groq references
   - Remove unused environment variables

---

## ✅ KEEP - Core E2E Working Components

### Routers (7 essential)
1. ✅ `/routers/users.py` - Authentication & user management
2. ✅ `/routers/appointments.py` - Appointment CRUD
3. ✅ `/routers/services.py` - Service management
4. ✅ `/routers/tenants.py` - Tenant management
5. ✅ `/routers/assistants.py` - Vapi assistant config
6. ✅ `/routers/api_keys.py` - Tenant BYOK
7. ✅ `/routers/vapi.py` - Vapi webhooks (CRITICAL)
8. ✅ `/routers/phone_numbers.py` - Phone number management
9. ✅ `/routers/websocket.py` - Real-time updates
10. ✅ `/routers/conversations.py` - Call logs from Vapi

### Models (6 essential)
1. ✅ `/models/user.py`
2. ✅ `/models/tenant.py`
3. ✅ `/models/appointment.py`
4. ✅ `/models/service.py`
5. ✅ `/models/business/business_config.py`
6. ✅ `/models/business/api_keys.py`

### Services (6 essential)
1. ✅ `/services/user_service.py`
2. ✅ `/services/appointments_service.py`
3. ✅ `/services/assistant_service.py` - Vapi integration
4. ✅ `/services/vapi_service.py` - Vapi API client
5. ✅ `/services/provisioning.py` - Tenant provisioning
6. ✅ `/services/socket_manager.py` - WebSocket manager

### Utils (5 essential)
1. ✅ `/utils/config.py` - Settings (needs cleanup)
2. ✅ `/utils/datetime_utils.py` - Date/time helpers
3. ✅ `/utils/encryption.py` - API key encryption
4. ✅ `/utils/security.py` - Password hashing, JWT
5. ✅ `/utils/__init__.py`

### Database
1. ✅ `/database/mongo_config.py`
2. ✅ `/database/__init__.py`

### Data
1. ✅ `/data/tenants.py` - Seed data

### Middleware
1. ✅ `/middleware/error_handler.py`

---

## 🗑️ Files to Delete (Immediate)

### Directories
```bash
rm -rf livekit/
rm -rf ai/
rm -rf scripts/
```

### Routers
```bash
rm routers/chat.py
rm routers/whatsapp.py
rm routers/billing.py
rm routers/monitoring.py
rm routers/admin.py
rm routers/platform_keys.py
```

### Models
```bash
rm models/agent.py
rm models/conversation.py
```

### Services
```bash
rm services/conversation_service.py
rm services/email_service.py
rm services/stripe_service.py
rm services/mock_stripe_service.py
rm services/twilio_service.py
rm services/admin_service.py
```

### Utils
```bash
rm utils/error_logger.py
rm utils/text_formatter.py
```

### Tests
```bash
rm tests/test_client_flow.py
rm tests/test_phone_integration.py
rm tests/integration_health_check.py
```

### Cache & Misc
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
rm =0.8.0
```

---

## 📝 Update .gitignore

Add to `.gitignore`:
```gitignore
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
build/
dist/
*.egg-info/
```

---

## 🔧 Code Updates Required

### 1. Update `main.py`
Remove imports:
```python
# REMOVE these imports
from routers import (
    chat,
    whatsapp,
    billing,
    admin,
    monitoring,
    platform_keys,
)

# REMOVE these router registrations
app.include_router(billing.router, ...)
app.include_router(chat.router, ...)
app.include_router(whatsapp.router, ...)
app.include_router(admin.router, ...)
app.include_router(monitoring.router, ...)
app.include_router(platform_keys.router, ...)
```

### 2. Update `utils/config.py`
Remove:
```python
# REMOVE LiveKit section
LIVEKIT_URL: str = ""
LIVEKIT_API_KEY: str = ""
LIVEKIT_API_SECRET: str = ""
LIVEKIT_AGENT_QUEUE: str = ""
LIVEKIT_AGENT_NAME: str = ""

# REMOVE Groq section
GROQ_API_KEY: str = ""
```

### 3. Update `requirements.txt`
Keep only:
```txt
# Core FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
email-validator==2.3.0
slowapi==0.1.9

# Environment
python-dotenv==1.0.0

# Date/Time
pytz==2024.1
dateparser==1.2.0

# HTTP Clients
requests==2.31.0
aiohttp==3.9.1

# Database - MongoDB
pymongo==4.6.1
motor==3.3.2
dnspython==2.4.2

# Security
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
argon2-cffi==25.1.0

# WebSockets
websockets==12.0

# Testing (dev only)
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.26.0

# Production
gunicorn==21.2.0
```

---

## 📦 Final Structure (Clean)

```
backend/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies (cleaned)
├── Dockerfile                 # Container config
├── .env.example              # Example environment
├── .gitignore                # Updated
│
├── data/
│   └── tenants.py            # Seed data
│
├── database/
│   ├── __init__.py
│   └── mongo_config.py       # MongoDB connection
│
├── middleware/
│   └── error_handler.py      # Error middleware
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── tenant.py
│   ├── appointment.py
│   ├── service.py
│   └── business/
│       ├── __init__.py
│       ├── business_config.py
│       └── api_keys.py
│
├── routers/
│   ├── __init__.py
│   ├── users.py              # Auth
│   ├── appointments.py       # Appointments
│   ├── services.py           # Services
│   ├── tenants.py            # Tenants
│   ├── assistants.py         # Vapi assistant
│   ├── api_keys.py           # BYOK
│   ├── vapi.py              # Webhooks ⭐
│   ├── phone_numbers.py      # Phone mgmt
│   ├── websocket.py          # Real-time
│   └── conversations.py      # Call logs
│
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── appointments_service.py
│   ├── assistant_service.py
│   ├── vapi_service.py       # Vapi client ⭐
│   ├── provisioning.py
│   └── socket_manager.py
│
├── utils/
│   ├── __init__.py
│   ├── config.py             # Settings (cleaned)
│   ├── datetime_utils.py
│   ├── encryption.py
│   └── security.py
│
└── tests/
    └── test_new_user_scenario.py
```

---

## 📈 Expected Results

### Size Reduction
- **Before**: 319MB
- **After**: ~50MB (84% reduction)
- Cache removed: ~50MB
- Unused code: ~200MB+

### Code Quality
- ✅ Single responsibility (Vapi for AI, MongoDB for data)
- ✅ Clear E2E flow: Frontend → FastAPI → Vapi → MongoDB
- ✅ No dead code
- ✅ Reduced dependencies
- ✅ Faster deployments

### Maintenance
- ✅ Easier to understand
- ✅ Faster onboarding
- ✅ Clear architecture
- ✅ Better documented

---

## 🚀 Execution Order

1. **Backup** (optional but recommended)
   ```bash
   cp -r backend backend_backup_$(date +%Y%m%d)
   ```

2. **Remove cache files**
   ```bash
   find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   find backend -name "*.pyc" -delete
   ```

3. **Remove unused directories**
   ```bash
   rm -rf backend/livekit backend/ai backend/scripts
   ```

4. **Remove unused files**
   ```bash
   # (see detailed list above)
   ```

5. **Update .gitignore**
   ```bash
   # Add Python cache patterns
   ```

6. **Update main.py**
   - Remove unused router imports
   - Remove unused router registrations

7. **Update requirements.txt**
   - Remove LiveKit dependencies
   - Remove Groq dependencies

8. **Update utils/config.py**
   - Remove LiveKit settings
   - Remove Groq settings

9. **Test**
   ```bash
   pytest tests/test_new_user_scenario.py
   ```

10. **Commit**
    ```bash
    git add .
    git commit -m "refactor: massive cleanup - remove unused code and reduce size by 84%"
    git push
    ```

---

## ⚠️ Important Notes

1. **Do NOT remove** while cleaning:
   - `/routers/vapi.py` - Core webhook handler
   - `/services/vapi_service.py` - Vapi API client
   - `/services/assistant_service.py` - Assistant management
   - Any files with "appointment", "user", "tenant"

2. **The E2E flow is**:
   ```
   User → Frontend → FastAPI → Vapi (AI) → FastAPI Webhook → MongoDB
   ```

3. **After cleanup, test these endpoints**:
   - POST /api/v1/users/token (login)
   - GET /api/v1/appointments (list)
   - POST /api/v1/appointments (create)
   - POST /api/v1/vapi/webhook (Vapi webhook)
   - GET /api/v1/assistant/me (get assistant)

---

## 📞 Support

If any issues after cleanup, check:
1. Railway logs for import errors
2. Missing dependencies in requirements.txt
3. MongoDB connection
4. Vapi webhook URL still configured
