---
description: Run all services (ngrok, backend, frontend, LiveKit agent, MongoDB)
---

# How to Run the Complete CallFlow AI Stack

This guide walks you through starting **all** components required for the CallFlow AI Receptionist SaaS in a local development environment.

## Prerequisites
- Docker & Docker Compose installed
- `ngrok` installed and authenticated (`ngrok authtoken <YOUR_TOKEN>`)
- Environment variables defined in `backend/.env` (single source of truth)
- LiveKit Cloud credentials (already set in `.env`)

## Services Overview
| Service | Docker Compose Service | Port | Description |
|---|---|---|---|
| MongoDB | `mongo` | `27017` | Database for appointments, tenants, etc. |
| N8N | `n8n` | `5678` | Workflow engine (booking, calendar, notifications) |
| Backend (FastAPI) | `backend` | `8000` | API layer, business logic |
| Frontend (Next.js) | `frontend` | `3000` | Dashboard UI |
| LiveKit Agent (Python) | `livekit-agent` | — | Connects to LiveKit Cloud for voice interactions |
| Ngrok Tunnel | — | `4040` (web UI) | Exposes local services to the internet |

## Step‑by‑Step Startup
1. **Start Docker Compose**
   ```bash
   cd /home/montassar/Desktop/ai_receptionist
   docker compose up -d
   ```
   This brings up MongoDB, N8N, the FastAPI backend, the Next.js frontend, and the LiveKit agent container.

2. **Verify containers are healthy**
   ```bash
   docker compose ps
   ```
   All services should show `healthy` or `running`.

3. **Launch Ngrok tunnels** (run in a separate terminal):
   ```bash
   # Expose the FastAPI backend
   ngrok http 8000 --host-header=localhost
   # Expose the Next.js frontend (optional, for external demo)
   ngrok http 3000 --host-header=localhost
   ```
   Keep note of the HTTPS URLs; they will be used for webhook callbacks in N8N.

4. **Configure N8N webhook URLs**
   - Open the N8N UI at the ngrok URL you just received for port `5678` (e.g., `https://abcd1234.ngrok.io`).
   - Update any webhook nodes in your existing workflows to point to the new public URLs.

5. **Test the LiveKit Agent**
   - Open the LiveKit web UI (provided by the LiveKit Cloud console) and join the room `tenant_<your‑tenant‑id>`.
   - Click **Test Call** in the dashboard; you should hear the AI receptionist.

6. **Optional: Seed Demo Data**
   ```bash
   curl -X POST http://localhost:8000/api/seed-demo -H "Authorization: Bearer <master_key>"
   ```
   This creates a sample business, appointments, and a tenant.

## Quick One‑Liner (for power users)
```bash
cd /home/montassar/Desktop/ai_receptionist && docker compose up -d && ngrok http 8000 --host-header=localhost & ngrok http 3000 --host-header=localhost
```

---

**Tip:** Keep the terminal windows open for logs. Use `docker compose logs -f <service>` to tail a specific service.
