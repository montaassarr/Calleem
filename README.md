# 🤖 CallFlow AI - Multi-Tenant AI Receptionist

**The complete AI voice receptionist platform for businesses.**  
Built with **Next.js 15**, **FastAPI**, **MongoDB**, and **n8n**.

---

## ✨ What's New

### 🧪 Mock Billing System (Test $499/month Flow Locally)
Test your complete subscription flow **without real charges**:
- ✅ Mock Stripe checkout (instant success, $0 charges)
- ✅ 14-day trial simulation (100 minutes limit)
- ✅ Complete onboarding wizard (6 steps)
- ✅ Subscription management (all features unlocked)

**Quick test:** `python test_mock_billing_flow.py` ← Run E2E test in 30 seconds

---

## 🚀 Features

### Core Platform
- **AI Voice Agent**: Human-like conversations powered by Vapi & Groq
- **Smart Automations**: Auto-sync to Google Calendar, Airtable, HubSpot, & Slack via n8n
- **Multi-Tenancy**: Secure data isolation for every business client
- **Real-Time Dashboard**: Live call logs, analytics, and appointment management

### Billing & Subscriptions (NEW)
- **Mock Mode**: Test locally without real Stripe charges
- **14-Day Trial**: 100 minutes included for every new signup
- **Usage Tracking**: Monitor minutes used vs. trial limit
- **BYOK Model**: Bring Your Own Keys (Groq, VAPI, OpenAI)
- **Customer Portal**: Self-service subscription management

---

## 🛠️ Quick Start

### Option 1: Test Mock Billing (Recommended First)

```bash
# 1. Start services
cd backend && python main.py  # Terminal 1
cd frontend_next && npm run dev  # Terminal 2

# 2. Run E2E test
python test_mock_billing_flow.py

# 3. Manual test in browser
# Open: http://localhost:3000/signup
# Complete: signup → mock checkout → success → onboarding
```

**See:** `QUICK_TEST_GUIDE.md` for detailed testing instructions

### Option 2: Full Docker Setup

```bash
# Clone & setup
git clone https://github.com/your-repo/callflow-ai.git
cd callflow-ai
cp .env.example .env

# Run with Docker
docker-compose up --build -d

# Access services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- n8n Workflows: http://localhost:5678
```

---

## 📦 Deployment

### Production Checklist

Before deploying to production:

1. **Switch to Real Stripe**
   ```bash
   # In backend/.env
   STRIPE_MOCK_MODE=false
   STRIPE_SECRET_KEY=REDACTED
   STRIPE_WEBHOOK_SECRET=REDACTED
   ```

2. **Create Stripe Product**
   - Go to https://dashboard.stripe.com/products
   - Create "AI Receptionist Pro" at $499/month
   - Add 14-day trial period
   - Copy `prod_xxx` and `price_xxx` to .env

3. **Set Up Webhooks**
   - Add endpoint: `https://your-domain.com/api/v1/billing/webhook`
   - Events: `checkout.session.completed`, `invoice.paid`, etc.

4. **Deploy**
   - One-click deploy to **Railway** or **Render**:
   ```bash
   ./deploy-railway.sh
   # or
   ./deploy-render.sh
   ```

---
