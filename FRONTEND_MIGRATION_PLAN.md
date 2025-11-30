# Frontend Pages Migration Plan

## Overview
Migrating 17 pages from old Vite/React frontend to new Next.js dashboard structure.

## Pages to Migrate

### ✅ Already in Dashboard
- `/dashboard/appointments` - Already exists
- `/dashboard/services` - Already exists
- `/dashboard/conversations` - Already exists
- `/dashboard/settings` - Already exists
- `/dashboard/settings/api-keys` - Already exists (new)
- `/dashboard/voice-agent` - Already exists
- `/dashboard/whatsapp` - Already exists

### 📋 Need to Add/Update

#### Main Dashboard Pages
1. **Index.tsx** → `/dashboard/page.tsx` (Already exists, may need update)
2. **Schedule.tsx** → `/dashboard/schedule/page.tsx` (NEW)
3. **Help.tsx** → `/dashboard/help/page.tsx` (Already exists)

#### Settings Pages
4. **Settings/Business.tsx** → `/dashboard/settings/business/page.tsx` (NEW)
5. **Settings/AI.tsx** → `/dashboard/settings/ai/page.tsx` (NEW)
6. **Settings/Integrations.tsx** → `/dashboard/settings/integrations/page.tsx` (NEW)
7. **Settings/Team.tsx** → `/dashboard/settings/team/page.tsx` (NEW)

#### AI Receptionist Pages
8. **AIReceptionist/Index.tsx** → `/dashboard/ai-receptionist/page.tsx` (NEW)
9. **AIReceptionist/Test.tsx** → `/dashboard/ai-receptionist/test/page.tsx` (NEW)

#### Utility Pages
10. **ApiTest.tsx** → `/dashboard/api-test/page.tsx` (NEW - for testing)

### ❌ Skip These
- **Login.tsx** - Not needed (using `/auth/login` now)
- **NotFound.tsx** - Next.js has `not-found.tsx`

## Migration Strategy

### Option 1: Manual Migration (Recommended)
- Review each old page
- Adapt to Next.js App Router conventions
- Update API calls to use new `/api/v1/auth/*` endpoints
- Ensure tenant-scoped data fetching

### Option 2: Copy & Adapt
- Copy old pages to new structure
- Update imports and routing
- Fix TypeScript errors
- Test each page

## Key Changes Needed

### 1. Routing
```typescript
// OLD (React Router)
<Route path="/appointments" element={<Appointments />} />

// NEW (Next.js App Router)
/dashboard/appointments/page.tsx
```

### 2. API Calls
```typescript
// OLD
POST /api/v1/users/login

// NEW
POST /api/v1/auth/login
POST /api/v1/auth/signup
```

### 3. Authentication
```typescript
// OLD - useAuth() with user.tenant_id

// NEW - useAuth() with tenant directly
const { tenant } = useAuth();
```

### 4. Data Fetching
All data is now automatically scoped by `tenant_id` via `X-Tenant-ID` header.

## Priority Order

### Phase 1: Critical Pages
1. Dashboard home (`/dashboard/page.tsx`)
2. Appointments
3. Services
4. Settings/API Keys

### Phase 2: Important Pages
5. Schedule
6. Conversations
7. WhatsApp
8. Settings/Business

### Phase 3: Nice-to-Have
9. AI Receptionist
10. Help
11. API Test
12. Settings (AI, Integrations, Team)

## Notes

- **Cleanup Command Running**: User has a command deleting everything except `.env`
- **Old Frontend**: Will be removed, so pages need to be migrated or documented
- **New Structure**: All pages go under `/dashboard/*` for tenant access
- **Tenant-Only**: No user roles, each tenant is their own admin
