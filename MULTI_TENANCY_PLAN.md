# Multi-Tenant SaaS Implementation Plan

## 🎯 Goal
Transform the AI Receptionist into a proper multi-tenant SaaS where:
1. **You (Admin)** manage multiple client tenants
2. **Each client** gets their own isolated dashboard
3. **New clients** start with a fresh, empty dashboard
4. **Clients configure** their own business details and API keys
5. **Complete data isolation** between tenants

## 🏗️ Current Architecture Analysis

### Backend (Already Has Multi-Tenancy Support!)
✅ **Tenant Model** exists (`models/core/tenants.py`)
✅ **Admin endpoints** for tenant management (`routers/admin.py`)
✅ **Tenant CRUD** operations implemented
✅ **User model** has fields for tenant association

### Frontend (Needs Work)
❌ **No tenant context** in frontend_next
❌ **Shared data** across users
❌ **Missing pages** from old frontend
❌ **No onboarding flow** for new tenants

## 📋 Implementation Steps

### Step 1: Fix User-Tenant Relationship

**Backend Changes:**
1. Update `models/core/users.py`:
   - Add `tenant_id` (reference to tenant)
   - Add `business_name` (for display)
   
2. Update `routers/users.py` registration:
   - Auto-create tenant when user signs up
   - Link user to their tenant
   - Set `tenant_id` in user document

3. Update all data endpoints to filter by `tenant_id`:
   - Appointments
   - Conversations
   - Services
   - Config

**Example:**
```python
# In appointments endpoint
@router.get("/")
async def get_appointments(current_user: dict = Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id")
    appointments = await db.appointments.find({"tenant_id": tenant_id}).to_list()
    return appointments
```

### Step 2: Frontend Tenant Context

**Create Tenant Context:**
```typescript
// contexts/TenantContext.tsx
interface TenantContextType {
  tenantId: string;
  businessName: string;
  isConfigured: boolean;
  refreshTenant: () => void;
}
```

**Update API Client:**
```typescript
// lib/api.ts
// Automatically include tenant_id in requests
api.interceptors.request.use((config) => {
  const tenantId = localStorage.getItem('tenant_id');
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  return config;
});
```

### Step 3: Role-Based Routing

**Admin Routes** (`/admin/*`):
- `/admin/dashboard` - Overview of all tenants
- `/admin/tenants` - Manage tenants
- `/admin/users` - Manage all users
- `/admin/analytics` - System-wide analytics

**Tenant Routes** (`/dashboard/*`):
- `/dashboard` - Tenant's own dashboard
- `/dashboard/appointments` - Their appointments
- `/dashboard/conversations` - Their conversations
- `/dashboard/services` - Their services
- `/dashboard/settings` - Their configuration

### Step 4: Onboarding Flow for New Tenants

**First Login Experience:**
1. Check if `tenant.is_configured === false`
2. Show setup wizard:
   - Step 1: Business Details (name, phone, email, address)
   - Step 2: API Keys (Groq, Twilio, WhatsApp)
   - Step 3: Services (add their services)
   - Step 4: Business Hours
3. Save configuration
4. Redirect to dashboard

### Step 5: Migrate Pages from Old Frontend

**Pages to Migrate:**
- ✅ Login (already done)
- ✅ Dashboard/Index (already done)
- ❌ Appointments
- ❌ Conversations
- ❌ Services
- ❌ Schedule
- ❌ WhatsApp
- ❌ Settings (AI, Integrations, Team, Business, Notifications)
- ❌ Help
- ❌ AI Receptionist pages

**Migration Process:**
1. Copy component from `/frontend/src/pages/`
2. Convert to Next.js page in `/frontend_next/app/dashboard/`
3. Update API calls to use new API client
4. Add tenant context
5. Update styling to match new design system

### Step 6: Admin Panel

**Admin Dashboard Components:**
```
/admin
  /dashboard - Overview stats
  /tenants - List all tenants
    /[id] - Tenant details
  /users - All users across tenants
  /analytics - System analytics
```

**Tenant List View:**
- Show all tenants with status
- Quick actions (activate, deactivate, view)
- Search and filter
- Usage statistics per tenant

## 🔐 Data Isolation Strategy

### Database Level:
```javascript
// Every document has tenant_id
{
  _id: ObjectId(...),
  tenant_id: ObjectId(...),  // Reference to tenant
  // ... other fields
}
```

### API Level:
```python
# All queries filter by tenant_id
async def get_appointments(current_user: dict):
    tenant_id = current_user["tenant_id"]
    return await db.appointments.find({"tenant_id": tenant_id})
```

### Frontend Level:
```typescript
// Tenant context ensures all requests include tenant_id
const { tenantId } = useTenant();
const appointments = await api.get(`/appointments?tenant_id=${tenantId}`);
```

## 🧪 Testing Checklist

### Scenario 1: New Tenant Signup
1. User signs up with email/password
2. System creates tenant automatically
3. User redirected to onboarding wizard
4. User configures business
5. User sees fresh, empty dashboard

### Scenario 2: Existing Tenant Login
1. User logs in
2. System loads their tenant data
3. User sees their configured dashboard
4. User can only see their own data

### Scenario 3: Admin Access
1. Admin logs in
2. Redirected to admin panel
3. Can see list of all tenants
4. Can view each tenant's details
5. Can manage users per tenant

### Scenario 4: Data Isolation
1. Create tenant1 with appointment A
2. Create tenant2 with appointment B
3. Tenant1 login: sees only appointment A
4. Tenant2 login: sees only appointment B
5. Admin login: sees both appointments

## 📊 Database Schema Updates

### Users Collection:
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  hashed_password: String,
  role: "admin" | "owner" | "user",
  tenant_id: ObjectId,  // NEW: Reference to tenant
  business_name: String,  // NEW: For display
  created_at: Date,
  updated_at: Date
}
```

### Tenants Collection (Already Exists):
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  phone: String,
  address: String,
  status: "active" | "inactive" | "suspended",
  plan: "free" | "basic" | "pro" | "enterprise",
  is_configured: Boolean,  // NEW: Has completed setup
  config: {
    groq_api_key: String,
    twilio_sid: String,
    twilio_token: String,
    whatsapp_token: String,
    // ... other API keys
  },
  created_at: Date,
  updated_at: Date
}
```

### All Data Collections (Appointments, Conversations, Services, etc.):
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,  // REQUIRED: Filter by this
  // ... collection-specific fields
}
```

## 🚀 Implementation Priority

### Phase 1 (Critical - Do First):
1. Fix user registration to create tenant
2. Add tenant_id to all data queries
3. Create tenant context in frontend
4. Fix routing (admin vs tenant)

### Phase 2 (Important):
1. Migrate missing pages from old frontend
2. Build onboarding wizard
3. Add admin panel views

### Phase 3 (Enhancement):
1. Add analytics
2. Add billing/subscription management
3. Add tenant usage limits

## 📝 Notes

- **Admin user** should have `role: "admin"` and `tenant_id: null`
- **Tenant owners** have `role: "owner"` and their own `tenant_id`
- **Tenant users** have `role: "user"` and same `tenant_id` as owner
- All API endpoints (except auth) require tenant context
- Frontend should show different nav based on role

---

This plan ensures complete multi-tenancy with proper data isolation!
