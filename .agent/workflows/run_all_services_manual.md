---
description: Run all services (ngrok, backend, frontend, LiveKit agent, MongoDB, N8N) manually in separate terminals
---

# Manual Startup Guide for CallFlow AI Receptionist (4‑5 Terminals)

This guide explains how to launch each component of the platform **without Docker**, using separate terminal windows (or tabs). It assumes you have the required tools installed globally.

## Prerequisites
- **Python 3.11** with `pip` and a virtual environment for the backend and LiveKit agent.
- **Node 20+** and `pnpm`/`npm` for the Next.js frontend.
- **MongoDB** installed locally (`mongod` service).
- **N8N** installed globally (`npm i -g n8n`).
- **ngrok** installed and authenticated (`ngrok authtoken <YOUR_TOKEN>`).
- **LiveKit Cloud credentials** set in `backend/.env` (the single source of truth).
- Ensure the **backend/.env** file contains all required keys (OpenAI, ElevenLabs, Deepgram, LiveKit, MongoDB URI, etc.).

## Overview of Terminals
| Terminal | Service | Command | Port |
|---|---|---|---|
| 1 | MongoDB | `mongod --config /etc/mongod.conf` *(or start the system service)* | `27017` |
| 2 | N8N | `n8n start --tunnel` *(optional tunnel for external access)* | `5678` |
| 3 | Backend (FastAPI) | `cd backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000` | `8000` |
| 4 | Frontend (Next.js) | `cd frontend_next && pnpm install && pnpm dev` | `3000` |
| 5 (optional) | LiveKit Agent (Python) | `cd livekit-agent && source .venv/bin/activate && python -m parker_165` | — |
| 6 (optional) | Ngrok tunnels | See below | `4040` (web UI) |

> **Tip:** You can combine the LiveKit agent and ngrok steps into the same terminal if you prefer fewer windows.

## Step‑by‑Step Commands
### 1️⃣ Start MongoDB
```bash
# If MongoDB is installed as a service (Ubuntu/Debian)
sudo systemctl start mongod
# Or run directly (ensure the data directory exists)
mongod --dbpath ~/data/mongo --logpath ~/data/mongo/mongod.log --fork
```
Leave this terminal open and verify it’s running:
```bash
mongo --eval "db.runCommand({ ping: 1 })"
```

### 2️⃣ Start N8N
```bash
npm i -g n8n   # run once if not installed
n8n start
```
Open `http://localhost:5678` in a browser to confirm the UI loads.

### 3️⃣ Start the FastAPI Backend
```bash
cd /home/montassar/Desktop/ai_receptionist/backend
# Create/activate virtual env if not present
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API docs are reachable at `http://localhost:8000/docs`.

### 4️⃣ Start the Next.js Frontend
```bash
cd /home/montassar/Desktop/ai_receptionist/frontend_next
pnpm install   # or npm install
pnpm dev
```
Visit `http://localhost:3000` to see the dashboard.

### 5️⃣ (Optional) Start the LiveKit Agent
```bash
cd /home/montassar/Desktop/ai_receptionist/livekit-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Parker_165 is the agent entry point defined in AGENTS.md
python -m parker_165
```
The agent will connect to the LiveKit Cloud using credentials from `.env`.

### 6️⃣ (Optional) Open Ngrok Tunnels
Run these in a **separate** terminal (or background them with `&`):
```bash
# Expose the FastAPI backend
ngrok http 8000 --host-header=localhost
# Expose the Next.js frontend (optional, for external demo)
ngrok http 3000 --host-header=localhost
```
Copy the generated HTTPS URLs and update any webhook URLs in N8N accordingly.

## Quick One‑Liner (for power users)
If you really want to fire everything up from a single script, you can create a small shell script like:
```bash
#!/usr/bin/env bash
# start_mongo.sh
sudo systemctl start mongod
# start_n8n.sh
n8n start &
# start_backend.sh
cd /home/montassar/Desktop/ai_receptionist/backend && source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 &
# start_frontend.sh
cd /home/montassar/Desktop/ai_receptionist/frontend_next && pnpm dev &
# start_agent.sh (optional)
cd /home/montassar/Desktop/ai_receptionist/livekit-agent && source .venv/bin/activate && python -m parker_165 &
# start_ngrok.sh (optional)
ngrok http 8000 --host-header=localhost &
ngrok http 3000 --host-header=localhost &
wait
```
Make it executable (`chmod +x run_all.sh`) and run `./run_all.sh`.

---

**Remember:** Keep each terminal open to view logs and debug any issues. Use `Ctrl‑C` to stop a service.
