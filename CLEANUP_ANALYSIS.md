# Project Cleanup Analysis
## AI Receptionist - Unused Files Report

**Date:** December 4, 2025  
**Status:** Analysis Complete ✅

---

## Summary

This project has accumulated **~321MB** of unnecessary files, primarily from example projects and build artifacts.

### Quick Stats
- **Example directories to remove:** 321MB
- **Cache files:** ~3,800+ Python cache files
- **Unused routers:** 2 placeholder files
- **Unused frontend pages:** 1 duplicate page
- **Build artifacts:** .next/, test-results/, etc.

---

## 🗑️ Files/Directories to Remove

### 1. Example Projects (321MB) 🎯 **HIGH PRIORITY**

#### `/livekit_examples/` (321MB)
- **Purpose:** Example projects from LiveKit documentation
- **Status:** ✅ Safe to delete
- **Reason:** These are reference examples, not part of the actual application
- **Contains:**
  - agent-starter-react
  - multi-agent-python
  - python-agents-examples (drive-thru, role-playing, nutrition-assistant, etc.)
  - agents/ (LiveKit plugins and examples)

#### `/Parker_165/` (16KB)
- **Purpose:** Old agent testing directory
- **Status:** ✅ Safe to delete
- **Reason:** Appears to be old experimental code, not integrated into the main app

### 2. Backend Placeholder Files 🎯

#### `/backend/routers/vapi_webhooks.py`
```python
# Current content: Just a placeholder with no real functionality
router = APIRouter()

@router.post("/vapi/webhook")
async def vapi_webhook_placeholder():
    raise HTTPException(status_code=410, detail="Vapi integration removed")
```
- **Status:** ✅ Safe to delete
- **Reason:** System no longer uses Vapi, using LiveKit instead
- **Action:** Remove file + remove from main.py imports

#### `/backend/routers/phone_numbers.py`
```python
# Current content: Placeholder that returns 410 for all routes
router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def phone_numbers_placeholder():
    raise HTTPException(status_code=410, detail="Phone numbers managed through LiveKit")
```
- **Status:** ✅ Safe to delete
- **Reason:** Phone numbers now managed through LiveKit integration
- **Action:** Remove file + remove from main.py imports

### 3. Frontend Duplicate Pages 🎯

#### `/frontend_next/app/dashboard/ai-receptionist/page.tsx`
- **Purpose:** AI receptionist testing page
- **Status:** ✅ Safe to delete
- **Reason:** Duplicate of `/dashboard/voice-agent/chat`
- **Note:** Not linked in sidebar navigation
- **Action:** Remove entire directory

### 4. Cache Files & Build Artifacts

#### Python Caches
```bash
# Locations:
- backend/__pycache__/
- backend/routers/__pycache__/
- backend/models/__pycache__/
- livekit-agent-worker/__pycache__/
# Total: ~3,800 cache directories
```
- **Status:** ✅ Safe to delete (regenerates automatically)
- **Command:** `find . -type d -name "__pycache__" -exec rm -rf {} +`

#### Frontend Build Artifacts
```bash
- frontend_next/.next/           # Next.js build output
- frontend_next/test-results/    # Playwright test results
- frontend_next/playwright-report/  # Playwright HTML reports
```
- **Status:** ✅ Safe to delete (regenerates on `npm run dev` or `npm run build`)

### 5. Log Files

#### Backend Logs
```bash
- backend/logs/          # Application logs
- logs/local/            # Local development logs
- logs/diagnostics/      # Diagnostic logs
```
- **Status:** ⚠️ Review before delete
- **Reason:** May contain useful debugging info
- **Action:** Archive old logs, keep recent ones

### 6. Test Directories (Conditional)

#### `/backend/tests/`
- **Purpose:** Unit and integration tests
- **Status:** ⚠️ **KEEP** if tests are up-to-date
- **Action:** Review test files for outdated tests before removing

#### `/frontend_next/tests/`
- **Purpose:** Playwright E2E tests
- **Status:** ⚠️ **KEEP** if tests are up-to-date
- **Action:** Review test files before removing

---

## 📦 Old Model Structure

The `backend/models/` directory has subdirectories that may be part of an old structure:
```
models/
├── ai/
├── analytics/
├── appointments/
├── automations/
├── billing/
├── branding/
├── business/
├── communication/
├── core/
├── crm/
├── integrations/
├── staff/
└── system_logs/
```

**Status:** ⚠️ **REVIEW REQUIRED**
- These are currently used by the application (imports found)
- This is the organized structure (good architecture)
- **Keep these** - they're the active model definitions

---

## 🔧 Actions Required in `main.py`

### Remove Unused Router Imports

**Current (main.py lines ~130-260):**
```python
# REMOVE these imports - no longer needed:
from routers import vapi_webhooks  # ❌ Remove
from routers import phone_numbers  # ❌ Remove

# REMOVE these include_router calls:
app.include_router(vapi_webhooks.router, ...)  # ❌ Remove
app.include_router(phone_numbers.router, ...)  # ❌ Remove
```

### Keep These Routers (Active & Used):
- ✅ `webhook.router` - Twilio webhook handling
- ✅ `webhook_livekit.router` - LiveKit webhook handling
- ✅ `appointments.router` - Appointment CRUD
- ✅ `services.router` - Service management
- ✅ `users.router` - Authentication
- ✅ `conversations.router` - Conversation history
- ✅ `admin.router` - Admin panel
- ✅ `admin_analytics.router` - Analytics
- ✅ `voice_agent.router` - Voice agent endpoints
- ✅ `platform_keys.router` - API key management
- ✅ `automations.router` - Smart automations
- ✅ `whatsapp.router` - WhatsApp integration
- ✅ `tenants.router` - Multi-tenancy
- ✅ `api_keys.router` - User API keys
- ✅ `agents.router` - AI agent config (newly simplified)
- ✅ `billing.router` - Subscription management
- ✅ `monitoring.router` - Health checks
- ✅ `simple_setup.router` - Easy setup wizard
- ✅ `onboarding.router` - Voice provider onboarding

---

## 🚀 Cleanup Script Usage

```bash
# Run the automated cleanup script
cd /home/montassar/Desktop/ai_receptionist
./scripts/cleanup_unused_files.sh

# Or run manually step-by-step:

# 1. Remove example directories (321MB)
rm -rf livekit_examples/ Parker_165/

# 2. Clean Python caches
find backend livekit-agent-worker -type d -name "__pycache__" -exec rm -rf {} +
find backend livekit-agent-worker -name "*.pyc" -delete

# 3. Clean frontend builds
rm -rf frontend_next/.next/ frontend_next/test-results/ frontend_next/playwright-report/

# 4. Remove placeholder routers
rm backend/routers/vapi_webhooks.py backend/routers/phone_numbers.py

# 5. Remove duplicate frontend page
rm -rf frontend_next/app/dashboard/ai-receptionist/

# 6. Clean logs (optional)
rm -rf backend/logs/* logs/local/* logs/diagnostics/*
```

---

## 💾 Expected Space Savings

| Item | Size | Safe to Delete |
|------|------|---------------|
| livekit_examples/ | 321MB | ✅ Yes |
| Parker_165/ | 16KB | ✅ Yes |
| Python caches | ~50MB | ✅ Yes |
| Frontend builds | ~100MB | ✅ Yes |
| Placeholder files | <1KB | ✅ Yes |
| Old logs | Varies | ⚠️ Review |
| **Total** | **~470MB+** | |

---

## ⚠️ Important Notes

### DO NOT DELETE:
1. ❌ `backend/models/*` - Active model definitions (organized structure)
2. ❌ `backend/routers/*` (except vapi_webhooks.py and phone_numbers.py)
3. ❌ `frontend_next/components/*` - Reusable UI components
4. ❌ `livekit-agent-worker/*` - Active voice agent
5. ❌ `n8n_workflows/*` - Automation workflows
6. ❌ `.env` files - Environment configuration

### Review Before Deleting:
1. ⚠️ `backend/tests/*` - May have useful tests
2. ⚠️ `frontend_next/tests/*` - E2E tests
3. ⚠️ Log files - May contain debugging info

---

## 🔍 After Cleanup Verification

```bash
# 1. Test backend starts successfully
cd backend
python3 main.py
# Should start without import errors

# 2. Test frontend builds
cd ../frontend_next
npm run dev
# Should start on port 3000

# 3. Test agent worker
cd ../livekit-agent-worker
./start.sh
# Should connect to LiveKit

# 4. Check disk usage
du -sh /home/montassar/Desktop/ai_receptionist
# Should be ~470MB smaller
```

---

## 📋 Cleanup Checklist

- [ ] Backup important data (optional)
- [ ] Run cleanup script: `./scripts/cleanup_unused_files.sh`
- [ ] Remove placeholder routers from main.py
- [ ] Test backend: `cd backend && python3 main.py`
- [ ] Test frontend: `cd frontend_next && npm run dev`
- [ ] Test voice agent: `cd livekit-agent-worker && ./start.sh`
- [ ] Verify all features work
- [ ] Commit changes to git

---

**Generated by:** AI Receptionist Cleanup Analysis Tool  
**Last Updated:** December 4, 2025
