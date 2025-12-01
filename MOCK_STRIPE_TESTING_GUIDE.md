# 🧪 LOCAL TESTING GUIDE - Mock Stripe Mode

## Overview

Your AI Receptionist SaaS now has **MOCK STRIPE MODE** for complete local testing without real charges or Stripe API calls.

---

## 🎯 What's Been Implemented

### Backend
- ✅ **Mock Stripe Service** (`/backend/services/mock_stripe_service.py`)
  - Simulates all Stripe API calls
  - Instant payment success
  - No real charges ever made
  
- ✅ **Stripe Service Wrapper** (`/backend/services/stripe_service.py`)
  - Unified interface for mock/live mode
  - Env var `STRIPE_MOCK_MODE=true` for testing
  
- ✅ **Billing Router** (`/backend/routers/billing.py`)
  - `/api/v1/billing/checkout` - Create checkout session
  - `/api/v1/billing/mock-complete-checkout` - Complete mock payment
  - `/api/v1/billing/subscription` - Get subscription status
  - `/api/v1/billing/portal` - Customer portal (mock)
  - `/api/v1/billing/webhook` - Stripe webhooks (mock)

### Frontend
- ✅ **Mock Checkout Page** (`/app/payment/mock-checkout/page.tsx`)
  - TEST MODE banner
  - Simulated payment button
  - $0.00 charge today display
  
- ✅ **Success Page** (`/app/payment/success/page.tsx`)
  - Confetti animation 🎉
  - Plan details display
  - Auto-redirect to onboarding (5s)
  
- ✅ **Cancel Page** (`/app/payment/cancel/page.tsx`)
  - User-friendly cancellation message
  - "Try Again" option

### Database
- ✅ **Updated Tenant Model** with trial fields:
  - `stripe_customer_id`
  - `stripe_subscription_id`
  - `subscription_status`
  - `trial_start_date`, `trial_end_date`
  - `trial_minutes_used`, `trial_minutes_limit`

---

## 🚀 How to Test Locally

### Step 1: Set Environment Variables

Create or update `/backend/.env`:

```bash
# Enable Mock Mode (NO real Stripe API calls)
STRIPE_MOCK_MODE=true

# These can be fake values in mock mode
STRIPE_SECRET_KEY=REDACTED
STRIPE_WEBHOOK_SECRET=REDACTED
STRIPE_PRODUCT_ID=prod_mock_ai_receptionist
STRIPE_PRICE_ID=price_mock_499_monthly

# Database
MONGO_URI=mongodb://localhost:27017/ai_receptionist

# JWT
JWT_SECRET=REDACTED
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### Step 2: Start Backend

```bash
cd backend
python main.py
```

Look for this log message:
```
🧪 STRIPE MOCK MODE ENABLED - No real charges will be made
```

### Step 3: Start Frontend

```bash
cd frontend_next
npm run dev
```

---

## 🧪 Testing Flow

### Complete E2E Test (Signup → Payment → Onboarding)

#### 1. **Sign Up**

```
Navigate to: http://localhost:3000/signup

Fill in:
- Name: Test User
- Business Name: Test Business
- Email: test@example.com
- Password: Test123!@#
- Phone: +1234567890
```

#### 2. **Auto-Login & Redirect**

After signup, you'll be auto-logged in. The tenant is created with:
- `tenant_id`: Generated automatically
- `plan`: "free" (before payment)
- `status`: "active"

#### 3. **Initiate Checkout**

Add a button to trigger checkout (or call API directly):

```typescript
const handleStartTrial = async () => {
  const response = await api.post("/billing/checkout");
  window.location.href = response.checkout_url;
};
```

**Expected Response:**
```json
{
  "checkout_url": "http://localhost:3000/payment/mock-checkout?session_id=cs_mock_...",
  "session_id": "cs_mock_abc123def456",
  "is_mock": true
}
```

#### 4. **Mock Checkout Page**

You'll see:
- 🧪 TEST MODE banner
- Plan: Pro - Monthly ($499/month)
- Trial: 14 days free, 100 minutes
- Due Today: **$0.00**
- Button: "🧪 Simulate Payment"

**Click "Simulate Payment"**

This will:
1. Show loading state (2s delay)
2. Call `/api/v1/billing/mock-complete-checkout`
3. Update tenant with subscription
4. Redirect to success page

#### 5. **Success Page**

You'll see:
- ✅ Success checkmark with confetti 🎉
- "Welcome Aboard!"
- Plan details
- "What's Next?" checklist
- Auto-redirect to onboarding (5s countdown)

#### 6. **Verify Database**

Check your tenant document:

```javascript
db.tenants.findOne({email: "test@example.com"})
```

**Should show:**
```json
{
  "_id": "tenant_xxx",
  "email": "test@example.com",
  "plan": "pro",
  "stripe_customer_id": "cus_mock_...",
  "stripe_subscription_id": "sub_mock_...",
  "subscription_status": "trialing",
  "trial_start_date": ISODate("2025-12-01..."),
  "trial_end_date": ISODate("2025-12-15..."),
  "trial_minutes_used": 0,
  "trial_minutes_limit": 100,
  "onboarding_completed": false
}
```

---

## 🔍 API Testing with cURL

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User",
    "business_name": "Test Business",
    "phone": "+1234567890",
    "role": "owner"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!@#"
```

**Save the `access_token` from response.**

### 3. Create Checkout Session

```bash
curl -X POST http://localhost:8000/api/v1/billing/checkout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "checkout_url": "http://localhost:3000/payment/mock-checkout?session_id=cs_mock_...",
  "session_id": "cs_mock_abc123",
  "is_mock": true
}
```

### 4. Complete Mock Checkout

```bash
curl -X POST "http://localhost:8000/api/v1/billing/mock-complete-checkout?session_id=cs_mock_abc123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "subscription_id": "sub_mock_xyz789",
  "status": "trialing",
  "message": "🧪 Mock payment successful! No real charges made."
}
```

### 5. Get Subscription Status

```bash
curl -X GET http://localhost:8000/api/v1/billing/subscription \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "status": "trialing",
  "plan_name": "AI Receptionist Pro",
  "plan_price": "$499/month",
  "trial_end": "2025-12-15T10:00:00",
  "current_period_end": "2025-12-15T10:00:00",
  "cancel_at_period_end": false,
  "is_mock": true
}
```

---

## 🎭 Mock Mode Features

### What's Simulated

✅ **Customer Creation**
- Generates fake `cus_mock_` customer IDs
- Stores in memory (not real Stripe)

✅ **Checkout Sessions**
- Generates fake `cs_mock_` session IDs
- Returns mock checkout URL (localhost)

✅ **Subscriptions**
- Generates fake `sub_mock_` subscription IDs
- Status: "trialing" for 14 days
- Trial end date: current date + 14 days

✅ **Customer Portal**
- Generates fake `bps_mock_` portal session IDs
- Returns mock portal URL (localhost)

✅ **Webhooks**
- Simulates `checkout.session.completed`
- Simulates `invoice.paid`
- Simulates `customer.subscription.updated`
- Simulates `customer.subscription.deleted`

### What's NOT Done

❌ No real API calls to Stripe
❌ No real charges
❌ No real payment methods stored
❌ No real invoices generated
❌ No real webhook signatures (just JSON parsing)

---

## 📊 Testing Checklist

### Basic Flow
- [ ] Signup creates tenant with `tenant_id`
- [ ] Login returns JWT token
- [ ] Checkout creates mock session
- [ ] Mock checkout page displays correctly
- [ ] "Simulate Payment" button works
- [ ] Success page shows confetti
- [ ] Tenant updated with subscription fields
- [ ] Trial dates set correctly (14 days)
- [ ] Trial limits set (100 minutes)

### Database Verification
- [ ] `stripe_customer_id` populated
- [ ] `stripe_subscription_id` populated
- [ ] `subscription_status` = "trialing"
- [ ] `trial_start_date` = now
- [ ] `trial_end_date` = now + 14 days
- [ ] `trial_minutes_used` = 0
- [ ] `trial_minutes_limit` = 100

### API Endpoints
- [ ] POST `/billing/checkout` returns session
- [ ] POST `/billing/mock-complete-checkout` updates tenant
- [ ] GET `/billing/subscription` returns status
- [ ] POST `/billing/portal` returns portal URL
- [ ] POST `/billing/webhook` processes events

### Frontend Pages
- [ ] `/payment/mock-checkout` renders
- [ ] TEST MODE banner visible
- [ ] Plan details correct ($499, 14 days, 100 min)
- [ ] "Simulate Payment" button works
- [ ] `/payment/success` shows confetti
- [ ] Auto-redirect works (5s countdown)
- [ ] `/payment/cancel` renders

---

## 🔄 Switching to Production

When ready for real Stripe:

### 1. Update Environment Variables

```bash
# Disable mock mode
STRIPE_MOCK_MODE=false

# Add real Stripe keys
STRIPE_SECRET_KEY=REDACTED
STRIPE_WEBHOOK_SECRET=REDACTED

# Create product/price in Stripe dashboard, then add IDs
STRIPE_PRODUCT_ID=prod_YOUR_REAL_PRODUCT_ID
STRIPE_PRICE_ID=price_YOUR_REAL_PRICE_ID
```

### 2. Create Product in Stripe Dashboard

1. Go to https://dashboard.stripe.com/products
2. Click "Add product"
3. Name: "AI Receptionist Pro"
4. Price: $499/month
5. Recurring: Monthly
6. Trial period: 14 days
7. Copy `prod_xxx` and `price_xxx` IDs to .env

### 3. Set Up Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. URL: `https://your-domain.com/api/v1/billing/webhook`
4. Events:
   - `checkout.session.completed`
   - `invoice.paid`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy signing secret to `STRIPE_WEBHOOK_SECRET`

### 4. Test with Stripe Test Mode

Before going live, test with Stripe's test mode:
- Use test keys (`sk_test_`, `pk_test_`)
- Use test cards (4242 4242 4242 4242)
- Verify webhook events in Stripe dashboard

### 5. Go Live

- Switch to live keys
- Remove mock checkout page from production
- Update checkout flow to use real Stripe URLs
- Monitor Stripe dashboard for real payments

---

## 🐛 Troubleshooting

### "Mock mode not working"

**Check logs:**
```
🧪 STRIPE MOCK MODE ENABLED - No real charges will be made
```

If not present, verify `.env` has `STRIPE_MOCK_MODE=true`

### "Session not found"

Mock sessions are stored in memory only. If you restart the backend, sessions are lost. Complete checkout flow in one session.

### "Tenant not updated"

Check that `tenant_id` is in the session metadata. Verify logs show:
```
🧪 Mock subscription activated for tenant tenant_xxx
```

### "Webhook not processing"

In mock mode, webhooks just parse JSON (no signature verification). Check request body is valid JSON.

---

## 📝 Next Steps

After successful mock testing:

1. ✅ **Phase 2: Onboarding Wizard** (next implementation)
   - Multi-step setup after payment
   - API keys configuration
   - Business profile completion
   
2. ✅ **Phase 3: Trial Management**
   - Usage tracking (minutes)
   - Trial banner in dashboard
   - Limit enforcement
   
3. ✅ **Phase 4: Billing Dashboard**
   - Show subscription status
   - Usage stats
   - Customer portal integration

---

## 🎉 Success Criteria

You'll know mock mode is working when:

✅ You can complete signup → payment → success flow in < 30 seconds
✅ No real Stripe API calls are made
✅ Tenant document has all subscription fields populated
✅ Trial dates are 14 days in the future
✅ Success page shows confetti and redirects
✅ You can test repeatedly without side effects
✅ Logs show "🧪 Mock" prefixes on all billing operations

---

**Status:** ✅ Mock Stripe Implementation Complete  
**Mode:** 🧪 Test/Development Only  
**Safety:** 💯 No Real Charges Possible
