# Windows Startup Guide - AI Receptionist

## Quick Start (All Services)

All services are currently running:
- **MongoDB**: Running as Windows Service
- **Backend**: http://localhost:8000
- **Ngrok**: https://matha-nonexotic-eugenia.ngrok-free.dev
- **Frontend**: http://localhost:5173 (starting)

---

## Manual Startup Commands

### 1. Start MongoDB

```powershell
# Start MongoDB service
Get-Service MongoDB | Start-Service

# Verify MongoDB is running
Get-Service MongoDB
```

**Alternative** (if not installed as service):
```powershell
# Start MongoDB manually
mongod
```

---

### 2. Start Backend API

```powershell
# Navigate to backend directory
cd C:\Users\montassar\Desktop\ai-_receptionist\backend

# Start backend server
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**What it does:**
- Starts FastAPI server on port 8000
- Enables auto-reload on code changes
- Accessible at: http://localhost:8000
- API docs at: http://localhost:8000/docs

---

### 3. Start Ngrok (Public Tunnel)

```powershell
# Navigate to project root
cd C:\Users\montassar\Desktop\ai-_receptionist

# Start ngrok tunnel
ngrok http 8000
```

**What it does:**
- Creates public HTTPS tunnel to localhost:8000
- Required for WhatsApp webhook
- Shows public URL in terminal (e.g., https://xxx.ngrok-free.dev)

**To get ngrok URL:**
```powershell
# Query ngrok API
Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' | 
    Select-Object -ExpandProperty tunnels | 
    Select-Object -ExpandProperty public_url
```

---

### 4. Start Frontend

```powershell
# Navigate to frontend directory
cd C:\Users\montassar\Desktop\ai-_receptionist\frontend

# Start dev server
npm run dev
```

**What it does:**
- Starts Vite development server
- Accessible at: http://localhost:5173
- Hot module replacement enabled

---

### 5. Open MongoDB Compass (Optional)

```powershell
# Start MongoDB Compass (if installed)
Start-Process "C:\Program Files\MongoDB Compass\MongoDBCompass.exe"
```

**Connection String:**
```
mongodb://localhost:27017
```

**Database Name:**
```
ai_barber_receptionist
```

---

## One-Command Startup Script

Save this as `start-all.ps1`:

```powershell
# Start MongoDB
Write-Host "`n[1/4] Starting MongoDB..." -ForegroundColor Cyan
Get-Service MongoDB | Start-Service -ErrorAction SilentlyContinue

# Start Backend
Write-Host "[2/4] Starting Backend..." -ForegroundColor Cyan
Set-Location "C:\Users\montassar\Desktop\ai-_receptionist\backend"
Start-Process -FilePath "..\venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
    -WindowStyle Minimized

# Start Ngrok
Write-Host "[3/4] Starting Ngrok..." -ForegroundColor Cyan
Set-Location "C:\Users\montassar\Desktop\ai-_receptionist"
Start-Process -FilePath "ngrok" `
    -ArgumentList "http", "8000" `
    -WindowStyle Minimized

# Start Frontend
Write-Host "[4/4] Starting Frontend..." -ForegroundColor Cyan
Set-Location "C:\Users\montassar\Desktop\ai-_receptionist\frontend"
Start-Process -FilePath "npm" `
    -ArgumentList "run", "dev" `
    -WindowStyle Minimized

Write-Host "`nAll services starting..." -ForegroundColor Green
Write-Host "Wait 10 seconds for services to initialize..." -ForegroundColor Yellow

Start-Sleep -Seconds 10

# Show status
Write-Host "`n=== Service Status ===" -ForegroundColor Cyan

# Backend
try {
    Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 2 | Out-Null
    Write-Host "Backend:  RUNNING - http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "Backend:  STARTING..." -ForegroundColor Yellow
}

# Ngrok
try {
    $ngrok = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -TimeoutSec 2
    $url = $ngrok.tunnels[0].public_url
    Write-Host "Ngrok:    RUNNING - $url" -ForegroundColor Green
} catch {
    Write-Host "Ngrok:    STARTING..." -ForegroundColor Yellow
}

# Frontend (check process)
$frontend = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*vite*' }
if ($frontend) {
    Write-Host "Frontend: RUNNING - http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "Frontend: STARTING..." -ForegroundColor Yellow
}

Write-Host "`nAll services launched!" -ForegroundColor Green
Write-Host "Check above for any services still starting." -ForegroundColor Yellow
```

**To run:**
```powershell
.\start-all.ps1
```

---

## Stop All Services

```powershell
# Stop Backend
Get-Process python | Where-Object { $_.CommandLine -like '*uvicorn*' } | Stop-Process -Force

# Stop Ngrok
Get-Process ngrok | Stop-Process -Force

# Stop Frontend
Get-Process node | Where-Object { $_.CommandLine -like '*vite*' } | Stop-Process -Force

# Stop MongoDB (optional)
Get-Service MongoDB | Stop-Service

Write-Host "All services stopped" -ForegroundColor Green
```

---

## Troubleshooting

### Port Already in Use

**Backend (Port 8000):**
```powershell
# Find and kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

**Frontend (Port 5173):**
```powershell
# Find and kill process on port 5173
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process -Force
```

**Ngrok (Port 4040):**
```powershell
# Kill all ngrok processes
Get-Process ngrok | Stop-Process -Force
```

### Check Running Services

```powershell
# Check MongoDB
Get-Service MongoDB

# Check Backend
Get-Process python | Where-Object { $_.CommandLine -like '*uvicorn*' }

# Check Ngrok
Get-Process ngrok

# Check Frontend
Get-Process node | Where-Object { $_.CommandLine -like '*vite*' }
```

### View Logs

**Backend Logs:**
```powershell
Get-Content C:\Users\montassar\Desktop\ai-_receptionist\backend\logs\app.log -Tail 50 -Wait
```

**Ngrok Dashboard:**
```
http://localhost:4040
```

### MongoDB Connection Issues

```powershell
# Check MongoDB service status
Get-Service MongoDB

# Restart MongoDB
Restart-Service MongoDB

# Check MongoDB is listening
Get-NetTCPConnection -LocalPort 27017
```

---

## Environment Configuration

### Backend (.env)

Location: `backend/.env`

Key settings:
```env
# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_barber_receptionist

# WhatsApp
WHATSAPP_TOKEN=REDACTED
WHATSAPP_PHONE_NUMBER_ID=897432366779845
WHATSAPP_VERIFY_TOKEN=verifytokenmeta

# Groq AI
GROQ_API_KEY=REDACTED
GROQ_MODEL=llama-3.3-70b-versatile
```

### Frontend (.env)

Location: `frontend/.env`

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Frontend | http://localhost:5173 | React dashboard |
| Ngrok Tunnel | https://xxx.ngrok-free.dev | Public webhook URL |
| Ngrok Dashboard | http://localhost:4040 | Ngrok web interface |
| MongoDB | mongodb://localhost:27017 | Database connection |

---

## Quick Health Checks

```powershell
# Backend health
Invoke-RestMethod http://localhost:8000/health

# Get appointments
Invoke-RestMethod http://localhost:8000/api/v1/appointments/

# Get ngrok URL
(Invoke-RestMethod http://localhost:4040/api/tunnels).tunnels[0].public_url

# MongoDB ping
mongosh --eval "db.adminCommand('ping')"
```

---

## Development Workflow

### 1. Morning Startup

```powershell
# Run the startup script
.\start-all.ps1

# Or start manually:
Get-Service MongoDB | Start-Service
cd backend; ..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd ..; ngrok http 8000
cd frontend; npm run dev
```

### 2. During Development

- Backend auto-reloads on code changes (uvicorn `--reload`)
- Frontend hot-reloads automatically (Vite HMR)
- Check logs in terminal windows
- Use http://localhost:8000/docs for API testing

### 3. End of Day

```powershell
# Stop all services
Get-Process python,ngrok,node | Stop-Process -Force

# MongoDB can stay running as service
```

---

## Notes

- **Emojis Removed**: All emoji characters have been removed from backend code to prevent Windows console encoding errors
- **Venv Location**: Virtual environment is in project root: `venv/`
- **Logs Location**: Backend logs stored in: `backend/logs/app.log`
- **Auto-reload**: Backend and Frontend both support hot-reload during development

---

## Current Status (As of now)

✓ MongoDB: Running  
✓ Backend: Running on http://localhost:8000  
✓ Ngrok: Running on https://matha-nonexotic-eugenia.ngrok-free.dev  
⏳ Frontend: Starting on http://localhost:5173  

All services successfully started!
