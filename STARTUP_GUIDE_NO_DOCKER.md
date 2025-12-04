# 🚀 COMPLETE STARTUP GUIDE (No Docker - Direct Terminal)

**Updated:** December 3, 2025  
**For:** Development/Testing without Docker

---

## 📋 What Runs Where

| Service | How It Runs | Port |
|---------|-------------|------|
| MongoDB | System service | 27017 |
| N8N | Docker container | 5678 |
| Backend | Python (venv) in terminal | 8000 |
| Frontend | Node.js in terminal | 3000 |
| Agent Worker | Python (venv) in terminal | N/A |

**Only N8N uses Docker!** Everything else runs directly in terminals.

---

## ⚡ QUICK START (Automated)

### Start Everything (Backend + Frontend + N8N)

```bash
cd /home/montassar/Desktop/ai_receptionist
./scripts/start_all.sh
```

This script will:
1. ✅ Start MongoDB (system service)
2. ✅ Start N8N (Docker)
3. ✅ Create backend venv + install deps + start uvicorn
4. ✅ Install frontend deps + start Next.js
5. ✅ Show all service URLs
6. ✅ Tail logs from backend and frontend

**Leave this terminal running!** It will show live logs.

### Start Agent Worker (Separate Terminal)

```bash
# Open NEW terminal
cd /home/montassar/Desktop/ai_receptionist/livekit-agent-worker
./start.sh
```

This will:
1. ✅ Create venv for agent worker
2. ✅ Install LiveKit dependencies
3. ✅ Check backend is running
4. ✅ Start agent worker
5. ✅ Show connection logs

**Leave this terminal running too!** It shows agent activity.

---

## 🔧 MANUAL START (Step by Step)

If you want more control, start each service manually:

### 1. Start MongoDB

```bash
# Check if running
sudo systemctl status mongod

# If not running, start it
sudo systemctl start mongod

# Enable auto-start on boot (optional)
sudo systemctl enable mongod

# Verify
mongosh --eval "db.version()"
```

### 2. Start N8N (Docker)

```bash
# Check if container exists
docker ps -a | grep n8n

# Start existing container
docker start n8n

# Or create new container
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Verify
curl http://localhost:5678
```

### 3. Start Backend

```bash
# Terminal 1: Backend
cd /home/montassar/Desktop/ai_receptionist/backend

# Create venv (first time only)
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify:** Open http://localhost:8000/docs

### 4. Start Frontend

```bash
# Terminal 2: Frontend
cd /home/montassar/Desktop/ai_receptionist/frontend_next

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

**Expected output:**
```
   ▲ Next.js 14.x.x
   - Local:        http://localhost:3000
   - Ready in 2.5s
```

**Verify:** Open http://localhost:3000

### 5. Start Agent Worker

```bash
# Terminal 3: Agent Worker
cd /home/montassar/Desktop/ai_receptionist/livekit-agent-worker

# Quick start
./start.sh

# OR manual:
source venv/bin/activate
python main.py dev
```

**Expected output:**
```
INFO:callflow-worker:Starting CallFlow AI Multi-Tenant Agent Worker
INFO:livekit.agents:Worker started
INFO:livekit.agents:Waiting for jobs...
```

---

## 📊 Service Check Commands

### Check All Ports

```bash
# Check what's running on each port
sudo lsof -i :27017  # MongoDB
sudo lsof -i :5678   # N8N
sudo lsof -i :8000   # Backend
sudo lsof -i :3000   # Frontend
```

### Check Backend Health

```bash
# Backend API
curl http://localhost:8000/docs

# Backend health check
curl http://localhost:8000/health 2>/dev/null || echo "No health endpoint"
```

### Check Frontend

```bash
# Frontend home
curl -I http://localhost:3000
```

### Check MongoDB

```bash
# Connect to MongoDB
mongosh

# List databases
show dbs

# Use your database
use callflow_ai_saas

# Check collections
show collections
```

### Check N8N

```bash
# Check container status
docker ps | grep n8n

# Check N8N logs
docker logs n8n -f

# Access N8N UI
open http://localhost:5678
```

---

## 🛑 STOP SERVICES

### Stop Everything (Automated)

```bash
cd /home/montassar/Desktop/ai_receptionist
./scripts/stop_all.sh
```

### Stop Manually

```bash
# Stop backend (in backend terminal)
Ctrl+C

# Stop frontend (in frontend terminal)
Ctrl+C

# Stop agent worker (in agent terminal)
Ctrl+C

# Stop N8N
docker stop n8n

# Stop MongoDB (optional, usually keep running)
sudo systemctl stop mongod
```

---

## 🐛 TROUBLESHOOTING

### Port Already in Use

**Backend (8000):**
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Or specific process
pkill -f "uvicorn main:app"
```

**Frontend (3000):**
```bash
# Kill process on port 3000
sudo lsof -ti:3000 | xargs kill -9

# Or specific process
pkill -f "next dev"
```

### Backend Not Starting

**Check Python version:**
```bash
python3 --version  # Should be 3.10+
```

**Check .env file:**
```bash
cd backend
cat .env | grep -v "^#"  # Should show all env vars
```

**Check dependencies:**
```bash
cd backend
source venv/bin/activate
pip list | grep fastapi  # Should show fastapi installed
```

### Frontend Not Starting

**Check Node version:**
```bash
node --version  # Should be 18+
npm --version
```

**Clear cache and reinstall:**
```bash
cd frontend_next
rm -rf node_modules .next
npm install
npm run dev
```

### MongoDB Not Starting

**Check status:**
```bash
sudo systemctl status mongod
```

**View logs:**
```bash
sudo journalctl -u mongod -f
```

**Restart:**
```bash
sudo systemctl restart mongod
```

### Agent Worker Not Connecting

**Check backend is reachable:**
```bash
curl http://localhost:8000/voice-agent/tenant-config/test
```

**Check LiveKit credentials:**
```bash
cd livekit-agent-worker
cat .env | grep LIVEKIT
```

**Check Python packages:**
```bash
cd livekit-agent-worker
source venv/bin/activate
pip list | grep livekit
```

---

## 📁 Log Files

All logs are saved in `logs/` directory:

```bash
cd /home/montassar/Desktop/ai_receptionist

# View backend logs
tail -f logs/backend.log

# View frontend logs
tail -f logs/frontend.log

# View both together
tail -f logs/backend.log logs/frontend.log

# View agent worker logs (shown in terminal)
cd livekit-agent-worker
./start.sh  # Logs appear in terminal
```

---

## 🔄 RESTART SERVICES

### Restart Backend Only

```bash
# In backend terminal: Ctrl+C
# Then:
cd /home/montassar/Desktop/ai_receptionist/backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Restart Frontend Only

```bash
# In frontend terminal: Ctrl+C
# Then:
cd /home/montassar/Desktop/ai_receptionist/frontend_next
npm run dev
```

### Restart Agent Worker Only

```bash
# In agent worker terminal: Ctrl+C
# Then:
cd /home/montassar/Desktop/ai_receptionist/livekit-agent-worker
./start.sh
```

---

## ✅ TYPICAL WORKFLOW

### Daily Development

1. **Morning startup:**
```bash
# Terminal 1
cd /home/montassar/Desktop/ai_receptionist
./scripts/start_all.sh
# Leave running, shows logs

# Terminal 2
cd livekit-agent-worker
./start.sh
# Leave running, shows agent logs
```

2. **Work on code:**
- Backend auto-reloads (uvicorn --reload)
- Frontend auto-reloads (Next.js fast refresh)
- Agent worker needs manual restart for code changes

3. **Test:**
- Open http://localhost:3000
- Go to `/dashboard/voice-agent/test`
- Make a test call

4. **End of day:**
```bash
# Ctrl+C in both terminals
# Or use:
./scripts/stop_all.sh
```

---

## 🎯 READY TO TEST?

**Start everything:**
```bash
# Terminal 1: All services
./scripts/start_all.sh

# Terminal 2: Agent worker
cd livekit-agent-worker && ./start.sh
```

**Then test:**
1. Open http://localhost:3000
2. Login
3. Add Groq API key at `/dashboard/settings/api-keys`
4. Go to `/dashboard/voice-agent/test`
5. Click "Start Call" and speak!

---

## 📞 QUICK REFERENCE

| Service | URL | Check |
|---------|-----|-------|
| MongoDB | mongodb://localhost:27017 | `mongosh` |
| N8N | http://localhost:5678 | `docker ps` |
| Backend | http://localhost:8000 | `curl localhost:8000/docs` |
| Frontend | http://localhost:3000 | `curl -I localhost:3000` |
| Agent Worker | N/A | Check terminal output |

**Logs:**
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
- Agent: Terminal output

**Stop All:**
```bash
./scripts/stop_all.sh
```

---

**Questions?** Check the terminal outputs - they're your best debugging tool! 🚀
