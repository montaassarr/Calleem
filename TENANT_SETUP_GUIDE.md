# 🏢 AI RECEPTIONIST - COMPLETE TENANT SETUP GUIDE

## 📋 Overview

This guide explains how a tenant (business owner) should set up their AI Receptionist dashboard to get WhatsApp AI and Voice AI working.

---

## 🎯 **WHAT EACH TENANT NEEDS**

Every tenant needs to configure **3 core systems**:

### 1. **API Keys** (BYOK - Bring Your Own Keys)
- ✅ **VAPI.ai** (for Voice Agent calls)
- ✅ **Groq/OpenAI** (for AI conversations)
- ✅ **ElevenLabs** (optional, for voice synthesis)
- ✅ **Meta WhatsApp Cloud API** (for WhatsApp integration)

### 2. **WhatsApp Configuration**
- WhatsApp Business Phone Number ID
- Meta Cloud Access Token
- Webhook setup

### 3. **Voice AI Configuration**
- VAPI Assistant ID
- System prompts
- Voice settings

---

## 📂 **CURRENT DASHBOARD STRUCTURE**

### **Main Pages** (Sidebar)
```
📊 Dashboard (/)
   ↳ Overview stats, recent activities

📅 Appointments (/appointments)
   ↳ View/manage bookings (✅ ISOLATED by tenant_id)

✂️ Services (/services)
   ↳ Manage services offered (✅ ISOLATED by tenant_id)

💬 Conversations (/conversations)
   ↳ View AI chat history (✅ ISOLATED by tenant_id)

🤖 Agents (/agents)
   ↳ Manage AI agents (✅ ISOLATED by tenant_id)

🎙️ Voice AI (/voice-agent)
   ↳ Voice agent control room
   ├── Control Room (/voice-agent)
   ├── Voice Chat (/voice-agent/chat)
   ├── WebRTC Test (/voice-agent/test)
   └── Voice Settings (/voice-agent/settings) ⚠️ DUPLICATE

📱 WhatsApp (/whatsapp)
   ↳ WhatsApp & SMS integration setup

⚙️ Settings (/settings)
   ├── Settings Hub (/settings)
   ├── 🏢 Business Profile (/settings/business) ✅ FIXED
   ├── 🧠 AI Config (/settings/ai) ⚠️ OVERLAPS with Voice Settings
   ├── 🔌 Integrations (/settings/integrations)
   ├── 👥 Team (/settings/team)
   ├── 💳 Billing (/settings/billing)
   ├── ✂️ Services (/settings/services) ⚠️ DUPLICATE of /services
   └── 🕐 Hours (/settings/hours)
```

---

## ⚠️ **ISSUES TO FIX**

### **1. Duplicate Pages**
- `/dashboard/voice-agent/settings` vs `/dashboard/settings/ai` 
  - **Both allow editing system prompts!**
  - **Solution**: Consolidate into ONE page

- `/dashboard/services` vs `/dashboard/settings/services`
  - **Same functionality!**
  - **Solution**: Keep only `/dashboard/services`, remove from settings

### **2. Missing Pages**
- ❌ **No API Keys Management Page** 
  - Backend has `/api/v1/keys/*` endpoints
  - Need: `/dashboard/settings/api-keys/page.tsx`

---

## 🛠️ **STEP-BY-STEP TENANT SETUP FLOW**

Here's the **EXACT ORDER** a tenant should follow to get everything working:

### **STEP 1: Business Profile** ✅ DONE
**Page**: `/dashboard/settings/business`

**Configure**:
- Business Name
- Phone Number
- Email
- Address
- Timezone

**Status**: ✅ Already tenant-isolated (fixed today)

---

### **STEP 2: API Keys** ⚠️ NEEDS PAGE
**Page**: `/dashboard/settings/api-keys` (MISSING - TO BUILD)

**Required API Keys**:

#### **A. VAPI.ai** (Voice Calls)
1. Go to [VAPI.ai Dashboard](https://dashboard.vapi.ai)
2. Create account
3. Copy **Public Key** and **Private Key**
4. Paste in API Keys page

#### **B. Groq/OpenAI** (Text AI)
1. Go to [Groq Console](https://console.groq.com) OR [OpenAI Platform](https://platform.openai.com)
2. Create API key
3. Paste in API Keys page

#### **C. Meta WhatsApp Cloud** (WhatsApp)
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create/select WhatsApp Business App
3. Get:
   - **Phone Number ID**
   - **Access Token** (permanent token)
   - **Verify Token** (create your own secret)
4. Paste in API Keys page

---

### **STEP 3: WhatsApp Configuration** ✅ EXISTS
**Page**: `/dashboard/whatsapp`

**Configure**:
1. Webhook URL (auto-generated, copy to Meta dashboard)
2. Verify Token (enter in Meta dashboard)
3. Test by sending message to WhatsApp number

**Meta Dashboard Steps**:
```
1. Meta Developers → Your App → WhatsApp → Configuration
2. Webhook URL: [Copy from /dashboard/whatsapp page]
3. Verify Token: [Enter your secret]
4. Subscribe to: messages, message_status
5. Save
```

---

### **STEP 4: AI Configuration** ⚠️ CONSOLIDATE
**Page**: `/dashboard/settings/ai` (Keep this one)

**Configure**:
- AI Model (Groq Mixtral, GPT-4, etc.)
- Temperature (creativity level)
- System Prompt (how AI should behave)
- Greeting Message
- Tone (professional/friendly/casual)

**Remove**: `/dashboard/voice-agent/settings` (duplicate!)

---

### **STEP 5: Voice AI Setup** ✅ EXISTS
**Page**: `/dashboard/voice-agent`

**Configure**:
- VAPI Assistant ID
- Test voice calls
- View call history

**Test Flow**:
1. Go to `/dashboard/voice-agent/test`
2. Click "Start WebRTC Test"
3. Speak with AI agent
4. Check if responses are correct

---

### **STEP 6: Services & Hours**
**Pages**: 
- `/dashboard/services` (keep)
- `/dashboard/settings/hours`

**Configure**:
- Add services (Haircut, Beard Trim, etc.)
- Set prices and durations
- Configure business hours

---

### **STEP 7: Test Everything**

#### **Test WhatsApp**:
```
1. Send "Hello" to your WhatsApp business number
2. Check /dashboard/conversations for response
3. Try booking an appointment via WhatsApp
```

#### **Test Voice AI**:
```
1. Go to /dashboard/voice-agent
2. Enter customer phone number
3. Click "Start Call"
4. Phone should ring with AI agent
```

---

## 🔐 **TENANT ISOLATION STATUS**

### **✅ Confirmed Isolated** (Each tenant sees only their data):
- `/dashboard` - Dashboard stats
- `/dashboard/appointments` - Appointments
- `/dashboard/services` - Services
- `/dashboard/conversations` - Conversations
- `/dashboard/agents` - Agents
- `/dashboard/settings/business` - Business profile ✅ FIXED TODAY

### **⚠️ Needs Verification**:
- `/dashboard/voice-agent` - Voice calls
- `/dashboard/whatsapp` - WhatsApp config
- `/dashboard/settings/api-keys` - API keys (TO BUILD)

---

## 🚀 **NEXT STEPS (Implementation)**

### **Priority 1: Build API Keys Page**
Create: `/frontend_next/app/dashboard/settings/api-keys/page.tsx`

**Features**:
- List all API keys (masked)
- Add new key (provider, name, key)
- Validate key on save
- Delete key
- Show last used date

**Backend Ready**: `/api/v1/keys/*` endpoints exist

### **Priority 2: Consolidate Duplicate Pages**
- ❌ Remove `/dashboard/settings/services` → use `/dashboard/services`
- ❌ Remove `/dashboard/voice-agent/settings` → merge into `/settings/ai`

### **Priority 3: Simplify Sidebar**
```
Suggested Structure:
📊 Dashboard
📅 Appointments  
✂️ Services
💬 Conversations
🎙️ Voice AI
   ├── Control Room
   ├── Live Test
   └── Call History (only)
📱 WhatsApp
⚙️ Settings
   ├── Business Profile
   ├── 🔑 API Keys (NEW!)
   ├── 🧠 AI Configuration
   ├── 🕐 Business Hours
   ├── 👥 Team
   └── 💳 Billing
```

---

## 📝 **REFERENCE: Working Single-Tenant Example**

The commit `08bb681` had a working single-tenant frontend (`frontend/` folder) where:

1. **Environment Variables** stored API keys:
   ```env
   VITE_VAPI_PUBLIC_KEY=xxx
   VITE_GROQ_API_KEY=xxx
   VITE_TWILIO_ACCOUNT_SID=xxx
   ```

2. **Pages worked**:
   - `/ai-receptionist` - Control room
   - `/ai-receptionist/test` - Test chat
   - `/whatsapp` - WhatsApp setup
   - `/settings/ai` - AI configuration

3. **Key Difference**:
   - Old: **Single tenant**, keys in `.env`
   - New: **Multi-tenant**, keys in database per tenant

---

## 🎓 **SUMMARY FOR YOU**

To make your multi-tenant system work like the single-tenant version:

1. **Build `/dashboard/settings/api-keys`** page
2. Each tenant enters their own:
   - VAPI keys
   - Groq/OpenAI keys  
   - Meta WhatsApp keys
3. Backend encrypts and stores per `tenant_id`
4. All features now work isolated per tenant!

**The main difference**: Instead of hardcoding keys in `.env`, each tenant manages their own keys in the UI, stored encrypted in the database.
