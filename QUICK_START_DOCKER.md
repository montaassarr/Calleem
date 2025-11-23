# 🚀 AI Receptionist - Quick Start with New Docker Architecture

## ⚡ Super Quick Start (3 Steps)

### 1. Environment is Already Configured ✅
Your `.env` file has been created with your existing API keys:
- ✅ GROQ_API_KEY
- ✅ VAPI_API_KEY  
- ✅ WHATSAPP_TOKEN
- ✅ SECRET_KEY

### 2. Start Development Environment
```bash
./start-dev.sh
```

This will:
- Build all Docker images
- Start 5 containers (MongoDB, Backend, Frontend, Setup, Gateway)
- Initialize the database
- Enable hot reload for development

### 3. Access Your Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017

**Default Admin Login:**
- Email: `admin@example.com`
- Password: `changeme`

---

## 📋 What's Running?

When you run `./start-dev.sh`, these containers start:

| Container | Port | Purpose |
|-----------|------|---------|
| `ai-receptionist-mongodb` | 27017 | Database |
| `ai-receptionist-setup` | - | One-time DB init (exits) |
| `ai-receptionist-backend-dev` | 8000 | FastAPI with hot reload |
| `ai-receptionist-frontend-dev` | 5173 | Vite dev server with HMR |

---

## 🛠️ Common Commands

### View Logs
```bash
# All containers
docker-compose -f docker-compose.new.yml --profile dev logs -f

# Specific container
docker-compose -f docker-compose.new.yml logs -f backend-dev
docker-compose -f docker-compose.new.yml logs -f frontend-dev
```

### Stop Everything
```bash
./stop.sh
```

### Restart a Service
```bash
docker-compose -f docker-compose.new.yml restart backend-dev
```

### Check Container Status
```bash
docker-compose -f docker-compose.new.yml --profile dev ps
```

### Access Container Shell
```bash
# Backend
docker exec -it ai-receptionist-backend-dev bash

# MongoDB
docker exec -it ai-receptionist-mongodb mongosh -u admin -p SecurePassword123ChangeThis
```

---

## 🔄 Hot Reload

Both frontend and backend support hot reload:

- **Backend**: Edit any `.py` file in `backend/` → Auto-reloads
- **Frontend**: Edit any file in `frontend/src/` → Instant HMR update

---

## 🧪 Testing the Setup

### 1. Check Health Endpoints
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173
```

### 2. Test API
Visit http://localhost:8000/docs for interactive API documentation

### 3. Test Frontend
Open http://localhost:5173 in your browser

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5173

# Stop your existing services
# (You have npm run dev and ngrok running)
```

### Container Won't Start
```bash
# View logs
docker-compose -f docker-compose.new.yml logs <service-name>

# Rebuild
docker-compose -f docker-compose.new.yml build --no-cache <service-name>
```

### Database Connection Issues
```bash
# Check MongoDB logs
docker-compose -f docker-compose.new.yml logs mongodb

# Verify MongoDB is running
docker-compose -f docker-compose.new.yml ps mongodb
```

---

## 📚 Next Steps

1. **Stop your current services** (npm run dev, ngrok) to free up ports
2. **Run** `./start-dev.sh`
3. **Access** http://localhost:5173
4. **Review** `DOCKER_DEPLOYMENT.md` for detailed documentation

---

## 🎯 Production Deployment

When ready for production:

```bash
# 1. Update .env for production
ENVIRONMENT=production
DEBUG=False

# 2. Start production mode
./start-prod.sh
```

See `DOCKER_DEPLOYMENT.md` for complete production deployment guide.

---

## 📖 Documentation

- **Quick Overview**: `DOCKER_ARCHITECTURE_SUMMARY.md`
- **Complete Guide**: `DOCKER_DEPLOYMENT.md`
- **File Listing**: `NEW_FILES_LISTING.md`
- **Implementation Plan**: `implementation_plan.md` (artifact)

---

**Ready to go!** Run `./start-dev.sh` to get started! 🚀
