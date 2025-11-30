# Frontend Conversion Guide

## Summary
All duplicate old React pages have been removed. The Next.js dashboard now has a clean structure with existing pages that need minor updates for the new tenant-only authentication system.

## Current Dashboard Structure (Clean)

```
frontend_next/app/dashboard/
├── admin/                    # Admin pages
├── appointments/             # ✅ Appointments management
├── automations/              # Automations
├── conversations/            # ✅ Call history
├── help/                     # ✅ Help pages
├── onboarding/               # Onboarding flow
├── schedule/                 # ✅ Schedule management
├── services/                 # ✅ Services management
├── settings/                 # ✅ Settings pages
│   ├── api-keys/             # ✅ API Keys (NEW)
│   ├── business/             # Business settings
│   ├── ai/                   # AI settings
│   ├── integrations/         # Integrations
│   └── team/                 # Team management
├── voice-agent/              # Voice agent pages
├── whatsapp/                 # ✅ WhatsApp integration
├── layout.tsx                # Dashboard layout
└── page.tsx                  # ✅ Dashboard home
```

## Pages That Need Updates

### 1. Update Authentication Context

**File**: `frontend_next/contexts/AuthContext.tsx`

**Changes Needed**:
```typescript
// OLD
interface User {
  id: string;
  email: string;
  tenant_id: string;
  role: string;
}

// NEW
interface Tenant {
  id: string;
  fullname: string;
  email: string;
  phone: string;
  config: TenantConfig;
  plan: string;
  status: string;
}

// Update context
const AuthContext = createContext<{
  tenant: Tenant | null;  // Changed from 'user'
  login: (email: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}>({} as any);

// Update API calls
const login = async (email: string, password: string) => {
  const response = await fetch('/api/v1/auth/login', {  // Changed from /users/login
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('tenant', JSON.stringify(data));  // Store tenant data
  setTenant(data);
};

const signup = async (signupData: SignupData) => {
  const response = await fetch('/api/v1/auth/signup', {  // Changed from /users/register
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(signupData),
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('tenant', JSON.stringify(data));
  setTenant(data);
};
```

### 2. Update Signup/Login Pages

**File**: `frontend_next/app/signup/page.tsx`

**Form Fields**:
```typescript
interface SignupForm {
  fullname: string;        // NEW (was full_name)
  email: string;
  password: string;
  phone: string;           // NEW (required)
  business_name: string;   // NEW (required)
}
```

**API Call**:
```typescript
POST /api/v1/auth/signup
{
  "fullname": "John Doe",
  "email": "john@barbershop.com",
  "password": "SecurePass123!",
  "phone": "+1234567890",
  "business_name": "John's Barber Shop"
}
```

### 3. Update API Client

**File**: `frontend_next/lib/api.ts`

Already updated to include `X-Tenant-ID` header ✅

### 4. Update All Dashboard Pages

**Pattern to Follow**:
```typescript
// OLD
import { useAuth } from '@/contexts/AuthContext';

const MyPage = () => {
  const { user } = useAuth();
  const tenantId = user.tenant_id;
  
  // ...
};

// NEW
import { useAuth } from '@/contexts/AuthContext';

const MyPage = () => {
  const { tenant } = useAuth();
  const tenantId = tenant.id;
  
  // ...
};
```

### 5. Pages to Update (Priority Order)

#### High Priority
1. **Dashboard Home** (`page.tsx`)
   - Update to use `tenant` instead of `user`
   - Show business name from `tenant.config.business_name`

2. **Appointments** (`appointments/page.tsx`)
   - Already tenant-scoped via API
   - Just update context usage

3. **Services** (`services/page.tsx`)
   - Already tenant-scoped via API
   - Just update context usage

4. **Settings/API Keys** (`settings/api-keys/page.tsx`)
   - Already created ✅
   - No changes needed

#### Medium Priority
5. **Conversations** (`conversations/page.tsx`)
   - Update context usage
   - Already tenant-scoped

6. **WhatsApp** (`whatsapp/page.tsx`)
   - Update context usage
   - Already tenant-scoped

7. **Voice Agent** (`voice-agent/page.tsx`)
   - Update context usage

#### Low Priority
8. **Settings Pages** (business, ai, integrations, team)
   - Update context usage
   - Add tenant-specific configuration

9. **Help** (`help/page.tsx`)
   - Minimal changes needed

10. **Schedule** (`schedule/page.tsx`)
    - Update context usage

## Quick Find & Replace

### Across All Files
```bash
# In frontend_next/app/dashboard/
find . -name "*.tsx" -type f -exec sed -i 's/const { user }/const { tenant }/g' {} +
find . -name "*.tsx" -type f -exec sed -i 's/user\.tenant_id/tenant.id/g' {} +
find . -name "*.tsx" -type f -exec sed -i 's/user\.email/tenant.email/g' {} +
find . -name "*.tsx" -type f -exec sed -i 's/user\.full_name/tenant.fullname/g' {} +
```

## Testing Checklist

After updates, test:
- [ ] Signup with new fields (fullname, phone, business_name)
- [ ] Login with email/password
- [ ] Dashboard shows correct tenant data
- [ ] All pages load without errors
- [ ] Data is tenant-scoped (no cross-tenant access)
- [ ] API keys can be configured
- [ ] Appointments CRUD works
- [ ] Services CRUD works
- [ ] Conversations display correctly

## Environment Variables

Update `.env`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Next Steps

1. Update `AuthContext.tsx` with new tenant structure
2. Update signup/login pages with new fields
3. Run find & replace for context usage
4. Test each page individually
5. Fix any TypeScript errors
6. Test full flow: signup → dashboard → API keys → voice call

## Notes

- **No user roles** - Each tenant is their own admin
- **Phone required** - Used for n8n tenant lookup
- **Business name required** - Stored in tenant config
- **All data auto-scoped** - Via `X-Tenant-ID` header
- **API keys encrypted** - Stored securely in MongoDB
