# MongoDB Updates Summary

## Changes Made

### 1. Database Indexes (mongo_config.py)
Updated all indexes to be **tenant-aware** for better multi-tenant data isolation and query performance:

#### Tenants Collection
- `email` (unique)
- `phone` (unique) - for n8n tenant lookup
- `owner_id` - reference to user
- `created_at` (descending)
- `status` - active/suspended/canceled

#### Users Collection
- `email` (unique)
- `username` (unique)
- `tenant_id` - for user-tenant association
- `(tenant_id, role)` - compound index for role-based queries

#### Appointments Collection (Tenant-Scoped)
- `(tenant_id, client_phone)` - find appointments by phone
- `(tenant_id, datetime)` - time-based queries
- `(tenant_id, status)` - filter by status
- `(tenant_id, datetime, status)` - compound for complex queries

#### Conversations Collection (Tenant-Scoped)
- `(tenant_id, phone_number)` - find conversations by phone
- `(tenant_id, created_at)` - chronological ordering
- `(tenant_id, call_id)` - lookup by call ID

#### Services Collection (Tenant-Scoped)
- `(tenant_id, name)` (unique) - prevent duplicate service names per tenant
- `(tenant_id, active)` - filter active services

### 2. Tenant Model Updates (tenant.py)

#### New Fields
- `owner_id`: Reference to the User who created the tenant
- `phone`: **Required** field for n8n tenant lookup by phone number
- `plan`: Subscription tier (free, basic, pro)
- `status`: Account status (active, suspended, canceled)
- `total_calls`: Usage tracking for billing
- `total_minutes`: Call duration tracking
- `updated_at`: Last modification timestamp
- `is_configured`: Boolean flag when API keys are set
- `elevenlabs_key`: Added to ApiKeys model for ElevenLabs voice AI support

#### Benefits
- **Multi-tenancy**: All data is isolated by `tenant_id`
- **Performance**: Compound indexes optimize common queries
- **Scalability**: Efficient queries even with millions of records
- **n8n Integration**: Phone-based tenant lookup for voice calls
- **Usage Tracking**: Built-in metrics for subscription management

### 3. Migration Notes

#### For Existing Data
If you have existing data, you'll need to:
1. Add `tenant_id` to all appointments, conversations, and services
2. Create a default tenant for existing users
3. Rebuild indexes

#### Migration Script (Optional)
```python
# Run this in MongoDB shell or via script
db.appointments.updateMany({}, {$set: {tenant_id: "DEFAULT_TENANT_ID"}})
db.conversations.updateMany({}, {$set: {tenant_id: "DEFAULT_TENANT_ID"}})
db.services.updateMany({}, {$set: {tenant_id: "DEFAULT_TENANT_ID"}})
```

### 4. API Changes Required

#### User Registration
- Must create a Tenant document when user signs up
- User's `tenant_id` must reference the created tenant
- Tenant's `owner_id` must reference the user

#### All Data Queries
- Must include `tenant_id` filter
- Use `X-Tenant-ID` header from requests
- Validate user belongs to tenant before operations

### 5. Performance Impact
- **Positive**: Compound indexes dramatically improve query speed
- **Minimal**: Index creation is one-time cost
- **Scalable**: Supports millions of tenants efficiently
