# AI Receptionist - Quick Start Reference

## 🚀 Three Ways to Start the Application

### Option 1: Docker (Recommended for Production)

**Best for:** Production deployment, consistent environment, easy setup

```bash
./docker-start.sh
```

**What it does:**
- Starts MongoDB, Backend, and Frontend in containers
- Handles all dependencies automatically
- No need to install Python, Node.js, or MongoDB locally

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**Stop:**
```bash
./docker-stop.sh
```

---

### Option 2: Local Development (start.sh)

**Best for:** Development with hot-reload, debugging

```bash
./start.sh
```

**Requirements:**
- Python 3.11+ installed
- Node.js 18+ installed
- MongoDB running locally

**What it does:**
- Checks MongoDB status
- Starts backend with uvicorn (hot-reload enabled)
- Starts frontend with Vite dev server

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

### Option 3: Manual Start

**Best for:** Fine-grained control, troubleshooting

#### Backend:
```bash
cd backend
source venv/bin/activate  # or .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```bash
cd frontend_next
npm run dev
```

---

## 📋 Quick Comparison

| Feature | Docker | start.sh | Manual |
|---------|--------|----------|--------|
| Setup Time | Fast | Medium | Slow |
| Dependencies | None (containerized) | Must install | Must install |
| Hot Reload | No | Yes | Yes |
| Production Ready | ✅ Yes | ❌ No | ❌ No |
| Debugging | Harder | Easy | Easiest |
| MongoDB | Included | Local required | Local required |

---

## 🔧 Environment Setup

### For Docker:
- Ensure `.env` exists in root directory
- Ensure `backend/.env` exists

### For Local Development:
- Create Python virtual environment
- Install dependencies: `pip install -r backend/requirements.txt`
- Install Node modules: `cd frontend_next && npm install`
- Start MongoDB: `sudo systemctl start mongod`

---

## 🆘 Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker info

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Local Development Issues
```bash
# Check MongoDB
sudo systemctl status mongod

# Check Python version
python3 --version

# Check Node version
node --version

# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd frontend_next && npm install
```

---

## 📖 More Information

- **Docker Guide**: [DOCKER.md](DOCKER.md)
- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Main README**: [README.md](README.md)
- **API Documentation**: http://localhost:8000/docs
