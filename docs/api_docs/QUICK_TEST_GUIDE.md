# 🚀 QUICK START - Test Your Mock Billing System

**Time to complete:** 5 minutes  
**No real charges:** 100% safe testing

---

## ⚡ Option 1: Automated Test Script (Recommended)

### Run the Complete E2E Test

```bash
cd /home/montassar/Desktop/ai_receptionist
python test_mock_billing_flow.py
```

This will automatically test:
1. ✅ User Registration
2. ✅ User Login
3. ✅ Checkout Session Creation
4. ✅ Mock Payment Completion
5. ✅ Subscription Verification
6. ✅ Tenant Database Update
7. ✅ Customer Portal Access

**Expected output:**
```
🧪 MOCK BILLING FLOW - COMPLETE E2E TEST
==================================================

Step 1/7: User Registration
✅ User registered successfully
ℹ️  User ID: 6587abc123def...
ℹ️  Tenant ID: 6587xyz789...

Step 2/7: User Login
✅ Login successful

Step 3/7: Create Checkout Session
✅ Checkout session created
⚠️  🧪 MOCK MODE - No real charges will be made

Step 4/7: Complete Mock Checkout
✅ Payment completed successfully
✅ 🧪 Mock payment successful! No real charges made.

Step 5/7: Verify Subscription Status
✅ Subscription verified
ℹ️  Status: trialing
ℹ️  Plan: AI Receptionist Pro - $499/month

...

📊 TEST SUMMARY
✅ ALL TESTS PASSED (7/7)
🎉 Mock billing system is working perfectly!
```

---

## 🖱️ Option 2: Manual Browser Testing

### 1. Start Services

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend_next
npm run dev
```

### 2. Test the Flow

#### A. Sign Up
```
Navigate to: http://localhost:3000/signup

Fill in:
- Name: Test User
- Email: test@example.com
- Password: Test123!@#
- Business Name: Test Business
- Phone: +1234567890
```

#### B. Login (if not auto-logged in)
```
Navigate to: http://localhost:3000/login
Use credentials from step A
```

#### C. Go to Checkout
```
Option 1: API call (cURL)
curl -X POST http://localhost:8000/api/v1/billing/checkout \
  -H "Authorization: Bearer YOUR_TOKEN"

Option 2: Add button to dashboard (temporary):
<Button onClick={async () => {
  const res = await api.post("/billing/checkout");
  window.location.href = res.checkout_url;
}}>
  Start Trial
</Button>
```

#### D. Mock Checkout Page
```
You'll see:
- 🧪 TEST MODE banner
- Plan: Pro - Monthly ($499/month)
- Trial: 14 days free, 100 minutes
- Due Today: $0.00

Click: "🧪 Simulate Payment"
Wait: 2 seconds
Redirect: Automatic to success page
```

#### E. Success Page
```
You'll see:
- ✅ Checkmark + Confetti 🎉
- "Welcome Aboard!"
- Plan details
- Auto-redirect to /onboarding (5s countdown)
```

#### F. Onboarding Wizard
```
Complete 6 steps:
1. Welcome screen
2. API Keys (Groq, VAPI)
3. Business Profile
4. n8n URL
5. Create Agent
6. Test Call

Enable test mode for pre-filled data:
http://localhost:3000/onboarding?test_mode=true
```

---

## 🔍 Verify Everything Works

### Check Database

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/ai_receptionist

# Check tenant
db.tenants.findOne({email: "test@example.com"})

# Should show:
{
  "_id": ObjectId("..."),
  "plan": "pro",
  "stripe_customer_id": "cus_mock_...",
  "stripe_subscription_id": "sub_mock_...",
  "subscription_status": "trialing",
  "trial_start_date": ISODate("2025-12-01..."),
  "trial_end_date": ISODate("2025-12-15..."),  // 14 days later
  "trial_minutes_used": 0,
  "trial_minutes_limit": 100,
  "onboarding_completed": false  // until wizard completed
}
```

### Check Backend Logs

```bash
# Look for these messages:
🧪 STRIPE MOCK MODE ENABLED - No real charges will be made
✅ Created mock checkout session: cs_mock_...
✅ Mock subscription activated for tenant tenant_...
```

### Test API Endpoints

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Create checkout (needs auth)
curl -X POST http://localhost:8000/api/v1/billing/checkout \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Get subscription status
curl http://localhost:8000/api/v1/billing/subscription \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Customer portal
curl -X POST http://localhost:8000/api/v1/billing/portal \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Criteria

You know it's working when:

### Backend
- ✅ Logs show "🧪 STRIPE MOCK MODE ENABLED"
- ✅ Checkout creates session with `cs_mock_` prefix
- ✅ Subscription has `sub_mock_` prefix
- ✅ Customer has `cus_mock_` prefix
- ✅ No real Stripe API calls made

### Frontend
- ✅ Mock checkout page displays TEST MODE banner
- ✅ Payment simulation completes in 2 seconds
- ✅ Success page shows confetti
- ✅ Auto-redirect to onboarding works
- ✅ Onboarding wizard shows 6 steps

### Database
- ✅ Tenant has `subscription_status` = "trialing"
- ✅ Trial dates are 14 days apart
- ✅ Trial limits set (100 minutes)
- ✅ Stripe IDs populated (with mock_ prefix)

---

## 🐛 Troubleshooting

### "Stripe API key not set"
**Solution:** Add to `backend/.env`:
```bash
STRIPE_MOCK_MODE=true
STRIPE_SECRET_KEY=REDACTED
STRIPE_WEBHOOK_SECRET=whsec_fake
```

### "Tenant not found"
**Solution:** Make sure user signup completes successfully. Check MongoDB:
```bash
mongosh
use ai_receptionist
db.tenants.find().pretty()
```

### "Mock mode not enabled"
**Solution:** Restart backend after setting env var:
```bash
cd backend
python main.py
# Look for: 🧪 STRIPE MOCK MODE ENABLED
```

### "Confetti animation not working"
**Solution:** Install package:
```bash
cd frontend_next
npm install canvas-confetti
```

### "Session expired"
**Solution:** Mock sessions are in-memory only. Complete the flow in one run without restarting backend.

---

## 📝 Testing Checklist

Before marking complete:

- [ ] Automated test script passes (7/7 tests)
- [ ] Can sign up new user
- [ ] Can login successfully
- [ ] Checkout creates mock session
- [ ] Mock payment completes
- [ ] Success page shows confetti
- [ ] Tenant has subscription fields
- [ ] Trial dates correct (14 days)
- [ ] Onboarding wizard loads
- [ ] Can complete onboarding
- [ ] No real Stripe API calls
- [ ] All mock IDs have `mock_` prefix

---

## 🎯 Next Steps After Testing

Once mock mode works perfectly:

### 1. Complete Onboarding Features
- [ ] Connect onboarding API to backend
- [ ] Save API keys (encrypted)
- [ ] Save business profile
- [ ] Create first agent
- [ ] Test call integration

### 2. Build Trial Management
- [ ] Usage tracker (minutes)
- [ ] Trial banner in dashboard
- [ ] Limit enforcement
- [ ] Trial end notifications

### 3. Billing Dashboard
- [ ] Show subscription status
- [ ] Usage stats
- [ ] Customer portal button
- [ ] Upgrade/cancel options

### 4. Switch to Production
- [ ] Set `STRIPE_MOCK_MODE=false`
- [ ] Add real Stripe keys
- [ ] Create product in Stripe
- [ ] Set up webhooks
- [ ] Test with Stripe test cards
- [ ] Deploy to production

---

## 📚 Related Documentation

- Full Testing Guide: `MOCK_STRIPE_TESTING_GUIDE.md`
- Launch Analysis: `LAUNCH_READINESS_ANALYSIS.md`
- Visual Summary: `LAUNCH_QUICK_SUMMARY.md`
- Developer Guide: `DEVELOPER.md`

---

**Status:** ✅ Mock System Ready for Testing  
**Safety:** 💯 No Real Charges Possible  
**Time Saved:** Hours of Stripe setup before launch
