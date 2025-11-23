# AI Receptionist - Docker Deployment Guide

## 🎯 Overview

This guide covers deploying the AI Receptionist using a modern 5-container Docker architecture:

1. **MongoDB** - Database with persistence
2. **Backend** - FastAPI application
3. **Frontend** - React/Vite application  
4. **Gateway** - Traefik reverse proxy (production)
5. **Setup** - One-time database initialization

## 📋 Prerequisites

### Required Software
- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Git** (for cloning the repository)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Required API Keys
- **Groq API Key** - Get from [console.groq.com](https://console.groq.com/)
- **OpenAI API Key** (optional) - Get from [platform.openai.com](https://platform.openai.com/)
- **VAPI API Key** - Get from [vapi.ai](https://vapi.ai/)
- **WhatsApp Access Token** - Get from [developers.facebook.com](https://developers.facebook.com/)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai_receptionist
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.new.example .env

# Edit .env and fill in your API keys
nano .env  # or use your preferred editor
```

**Required variables to configure:**
- `MONGO_INITDB_ROOT_PASSWORD` - Set a strong password
- `SECRET_KEY` - Generate a secure random key (min 32 characters)
- `GROQ_API_KEY` - Your Groq API key
- `VAPI_API_KEY` - Your VAPI API key
- `WHATSAPP_TOKEN` - Your WhatsApp access token
- `WHATSAPP_PHONE_NUMBER_ID` - Your WhatsApp phone number ID
- `WHATSAPP_VERIFY_TOKEN` - Custom verify token for webhooks

### 3. Start Development Environment
```bash
./start-dev.sh
```

This will:
- Build all Docker images
- Start containers with hot reload
- Initialize the database
- Create default services and admin user

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `changeme` (⚠️ Change immediately!)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Gateway │ (Traefik - Production only)
                    │  :80    │
                    │  :443   │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │Frontend │     │ Backend │    │  VAPI   │
    │  :3000  │────▶│  :8000  │    │Webhooks │
    └─────────┘     └────┬────┘    └─────────┘
                         │
                    ┌────▼────┐
                    │ MongoDB │
                    │ :27017  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Setup  │ (One-time init)
                    └─────────┘
```

## 🔧 Development Mode

### Starting Development Environment
```bash
./start-dev.sh
```

**Features:**
- Hot reload for backend (code changes auto-reload)
- Hot reload for frontend (Vite HMR)
- Source code mounted as volumes
- Debug mode enabled
- Detailed logging

### Viewing Logs
```bash
# All containers
docker-compose -f docker-compose.new.yml --profile dev logs -f

# Specific container
docker-compose -f docker-compose.new.yml logs -f backend-dev
docker-compose -f docker-compose.new.yml logs -f frontend-dev
```

### Stopping Development Environment
```bash
./stop.sh
```

## 🏭 Production Deployment

### 1. Prepare Environment
```bash
# Copy and configure production environment
cp .env.new.example .env

# Edit with production values
nano .env
```

**Production-specific settings:**
```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
MONGO_INITDB_ROOT_PASSWORD=<strong-password>

# Optional: Configure domain for Traefik
DOMAIN=yourdomain.com
ACME_EMAIL=admin@yourdomain.com
```

### 2. Start Production Environment
```bash
./start-prod.sh
```

This will:
- Build optimized production images (no cache)
- Start containers in production mode
- Run with multiple workers
- Enable health checks
- Run in detached mode

### 3. Verify Deployment
```bash
# Check container status
docker-compose -f docker-compose.new.yml --profile prod ps

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:3000

# View logs
docker-compose -f docker-compose.new.yml --profile prod logs -f
```

### 4. Configure Reverse Proxy (Optional)

For production with a custom domain, configure Traefik:

1. Uncomment Traefik Let's Encrypt settings in `docker-compose.new.yml`
2. Set `DOMAIN` and `ACME_EMAIL` in `.env`
3. Configure DNS to point to your server
4. Restart containers

## 🌐 Cloud Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04, t3.medium or larger)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Clone and deploy
git clone <repository-url>
cd ai_receptionist
cp .env.new.example .env
nano .env  # Configure
./start-prod.sh

# 5. Configure security group to allow ports 80, 443
```

### Google Cloud Platform (GCP)

```bash
# 1. Create Compute Engine instance
gcloud compute instances create ai-receptionist \
    --machine-type=e2-medium \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud

# 2. SSH and install Docker
gcloud compute ssh ai-receptionist
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Deploy application
git clone <repository-url>
cd ai_receptionist
./start-prod.sh
```

### DigitalOcean

```bash
# 1. Create Droplet (Ubuntu 22.04, 4GB RAM)
# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker (usually pre-installed on Docker droplet)
# 4. Deploy
git clone <repository-url>
cd ai_receptionist
./start-prod.sh
```

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` to version control
- ✅ Use strong, unique passwords
- ✅ Rotate API keys regularly
- ✅ Use secrets management in production (AWS Secrets Manager, etc.)

### 2. MongoDB Security
```bash
# Change default MongoDB password
MONGO_INITDB_ROOT_PASSWORD=<strong-random-password>

# Restrict MongoDB port (don't expose publicly)
# Remove port mapping in docker-compose.yml for production
```

### 3. SSL/TLS
```bash
# Enable HTTPS with Let's Encrypt
# Uncomment Traefik ACME settings in docker-compose.new.yml
DOMAIN=yourdomain.com
ACME_EMAIL=admin@yourdomain.com
```

### 4. Firewall Configuration
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Block direct access to backend/MongoDB
sudo ufw deny 8000/tcp
sudo ufw deny 27017/tcp
```

## 🧪 Testing & Verification

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# MongoDB connection
docker exec ai-receptionist-mongodb mongosh \
  -u admin -p <password> --eval "db.adminCommand('ping')"
```

### Database Verification
```bash
# Check collections
docker exec ai-receptionist-mongodb mongosh \
  -u admin -p <password> ai_receptionist \
  --eval "db.getCollectionNames()"

# Check services
docker exec ai-receptionist-mongodb mongosh \
  -u admin -p <password> ai_receptionist \
  --eval "db.services.find().pretty()"
```

### API Testing
```bash
# Test appointment creation
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test User",
    "customer_phone": "+1234567890",
    "service": "Haircut",
    "appointment_date": "2025-12-01T10:00:00"
  }'
```

## 🔄 Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
./stop.sh
./start-prod.sh
```

### Database Backup
```bash
# Backup MongoDB
docker exec ai-receptionist-mongodb mongodump \
  -u admin -p <password> \
  --out /data/backup

# Copy backup to host
docker cp ai-receptionist-mongodb:/data/backup ./mongodb-backup
```

### Database Restore
```bash
# Copy backup to container
docker cp ./mongodb-backup ai-receptionist-mongodb:/data/restore

# Restore
docker exec ai-receptionist-mongodb mongorestore \
  -u admin -p <password> \
  /data/restore
```

### Viewing Container Logs
```bash
# All logs
docker-compose -f docker-compose.new.yml --profile prod logs

# Specific service
docker-compose -f docker-compose.new.yml logs backend

# Follow logs in real-time
docker-compose -f docker-compose.new.yml logs -f --tail=100
```

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker-compose -f docker-compose.new.yml logs <service-name>

# Check container status
docker-compose -f docker-compose.new.yml ps

# Rebuild container
docker-compose -f docker-compose.new.yml build --no-cache <service-name>
```

### Database Connection Issues
```bash
# Verify MongoDB is running
docker-compose -f docker-compose.new.yml ps mongodb

# Check MongoDB logs
docker-compose -f docker-compose.new.yml logs mongodb

# Test connection
docker exec ai-receptionist-mongodb mongosh \
  -u admin -p <password> --eval "db.adminCommand('ping')"
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill process or change port in .env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Permission Issues
```bash
# Fix log directory permissions
sudo chown -R $USER:$USER backend/logs

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

## 📊 Monitoring

### Container Resource Usage
```bash
# View resource usage
docker stats

# Specific container
docker stats ai-receptionist-backend
```

### Application Metrics
- Access `/health` endpoint for health status
- Check logs for errors and warnings
- Monitor MongoDB performance

## 🔗 Useful Commands

```bash
# Start development
./start-dev.sh

# Start production
./start-prod.sh

# Stop all containers
./stop.sh

# View logs
docker-compose -f docker-compose.new.yml logs -f

# Restart specific service
docker-compose -f docker-compose.new.yml restart backend

# Execute command in container
docker exec -it ai-receptionist-backend bash

# Clean up everything (including volumes)
docker-compose -f docker-compose.new.yml down -v
docker system prune -a
```

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review this documentation
3. Check GitHub issues
4. Contact support team

## 📝 License

[Your License Here]
