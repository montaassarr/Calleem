# 🤖 CallFlow AI - Multi-Tenant AI Receptionist

**The complete AI voice receptionist platform for businesses.**  
Built with **Next.js 14**, **FastAPI**, **MongoDB**, and **n8n**.

## 🚀 Features
- **AI Voice Agent**: Human-like conversations powered by Vapi & Groq.
- **Smart Automations**: Auto-sync to Google Calendar, Airtable, HubSpot, & Slack via n8n.
- **Multi-Tenancy**: Secure data isolation for every business client.
- **Real-Time Dashboard**: Live call logs, analytics, and appointment management.

## 🛠️ Quick Start
1. **Clone & Setup**:
   ```bash
   git clone https://github.com/your-repo/callflow-ai.git
   cd callflow-ai
   cp .env.example .env
   ```
2. **Run with Docker**:
   ```bash
   docker-compose up --build -d
   ```
3. **Access**:
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **n8n Workflows**: [http://localhost:5678](http://localhost:5678)

## 📦 Deployment
One-click deploy to **Railway** or **Render**:
- [Deploy to Railway](./deploy-railway.sh)
- [Deploy to Render](./deploy-render.sh)
