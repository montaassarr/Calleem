# Simplified Tenant-Only Architecture

## Overview
The architecture has been simplified to use **only Tenants** - no separate Users table. Each tenant is a business owner who logs in directly and has access to their own isolated dashboard.

## Key Changes

### 1. Tenant Model (`models/tenant.py`)
**New Structure:**
```python
class Tenant:
    # Authentication (built-in)
    fullname: str          # Business owner's name
    email: EmailStr        # Login email (unique)
    password: str          # Hashed password
    phone: str             # Business phone (unique, for n8n lookup)
    
    # Business config
    config: TenantConfig   # Business settings
    api_keys: ApiKeys      # Voice AI credentials
    
    # Subscription
    plan: str              # free, basic, pro
    status: str            # active, suspended, canceled
    total_calls: int       # Usage tracking
    total_minutes: float   # Call duration tracking
```

### 2. Authentication (`routers/auth.py`)
**New Endpoints:**
- `POST /api/v1/auth/signup` - Register new tenant
- `POST /api/v1/auth/login` - Tenant login
- `GET /api/v1/auth/me` - Get current tenant info

**Removed:**
- No separate users table
- No user roles (admin, owner, etc.)
- Each tenant is their own admin

### 3. Database Structure

**Collections:**
- `tenants` - Business owners with auth
- `appointments` - Scoped by `tenant_id`
- `conversations` - Scoped by `tenant_id`
- `services` - Scoped by `tenant_id`

**Removed:**
- `users` collection (merged into tenants)

### 4. Frontend Changes Required

**Update API Calls:**
```javascript
// OLD
POST /api/v1/users/register
POST /api/v1/users/login

// NEW
POST /api/v1/auth/signup
POST /api/v1/auth/login
```

**Signup Form Fields:**
```javascript
{
  fullname: "John Doe",
  email: "john@barbershop.com",
  password: "SecurePass123!",
  phone: "+1234567890",
  business_name: "John's Barber Shop"
}
```

**Login Form Fields:**
```javascript
{
  email: "john@barbershop.com",
  password: "SecurePass123!"
}
```

### 5. Dashboard Access
Each tenant gets access to **ALL** dashboard pages:
- `/dashboard` - Overview
- `/dashboard/appointments` - Manage appointments
- `/dashboard/services` - Manage services
- `/dashboard/conversations` - Call history
- `/dashboard/settings` - Business settings
- `/dashboard/settings/api-keys` - Configure voice AI

**Data Isolation:**
- All data is automatically filtered by `tenant_id`
- No cross-tenant data access
- Each tenant sees only their own data

### 6. Benefits

✅ **Simpler Architecture**
- One table for authentication
- No user-tenant relationship complexity
- Easier to understand and maintain

✅ **Better Performance**
- Fewer database queries
- No joins between users and tenants
- Direct tenant lookup

✅ **Cleaner Code**
- No role-based access control needed
- Simpler authentication flow
- Less middleware complexity

### 7. Migration from Old Structure

If you have existing data with separate users:

```javascript
// MongoDB migration script
db.users.find().forEach(user => {
  db.tenants.updateOne(
    { _id: user.tenant_id },
    {
      $set: {
        fullname: user.full_name,
        email: user.email,
        password: user.password,
        phone: user.phone || "+0000000000"
      }
    }
  );
});

// Drop users collection
db.users.drop();
```

### 8. API Endpoints Summary

**Authentication:**
- `POST /api/v1/auth/signup` - Create tenant account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current tenant

**Tenant Management:**
- `GET /api/v1/tenants/me` - Get tenant info
- `PUT /api/v1/tenants/me/config` - Update business config
- `PUT /api/v1/tenants/me/api-keys` - Update API keys
- `POST /api/v1/tenants/lookup-by-phone` - n8n tenant lookup
- `PATCH /api/v1/tenants/{id}/usage` - Update usage stats

**Data (All Tenant-Scoped):**
- `/api/v1/appointments/*` - Appointments
- `/api/v1/services/*` - Services
- `/api/v1/conversations/*` - Call history

### 9. Security Notes

- Passwords are hashed with Argon2
- API keys are encrypted with Fernet
- JWT tokens for authentication
- Phone numbers are unique (for n8n lookup)
- Email addresses are unique (for login)
