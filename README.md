# AI Receptionist - Full Stack Application

AI-powered receptionist system for managing appointments, conversations, and business operations.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - RESTful API
- **Frontend**: Next.js (React/TypeScript) - Dashboard UI
- **Database**: MongoDB - Data storage
- **Deployment**: Docker Compose for local development, Railway (backend) + Vercel (frontend) for production

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Git installed

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ai_receptionist
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env  # If you have an example file
# Or create .env manually
```

Minimum required environment variables:

```env
# Database
MONGO_URI=mongodb://mongodb:27017/ai_receptionist
MONGO_DB_NAME=ai_receptionist

# Security
SECRET_KEY=REDACTED  # Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'

# API Keys (optional for basic testing)
GROQ_API_KEY=REDACTED
OPENAI_API_KEY=REDACTED

# Environment
ENVIRONMENT=development
```

### Step 3: Build and Start Services

```bash
# From project root
docker-compose up -d --build
```

Or use the test script:

```bash
./scripts/test_docker.sh
```

### Step 4: Verify Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **MongoDB**: mongodb://localhost:27017

### Step 5: Test Endpoints

```bash
# Run comprehensive endpoint tests
python3 scripts/test_endpoints.py

# Or test manually
curl http://localhost:8000/health
curl http://localhost:8000/
```

## 📋 Docker Services

### Backend Service
- **Container**: `callflow-backend`
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Dependencies**: MongoDB

### Frontend Service
- **Container**: `callflow-frontend`
- **Port**: 3000
- **Dependencies**: Backend service

### MongoDB Service
- **Container**: `callflow-mongodb`
- **Port**: 27017
- **Volume**: `mongo_data` (persistent storage)

## 🧪 Testing

### Test All Endpoints

```bash
python3 scripts/test_endpoints.py
```

This will test all API endpoints and generate a report in `endpoint_test_results.json`.

### Test Docker Setup

```bash
./scripts/test_docker.sh
```

This script will:
1. Build Docker images
2. Start all services
3. Wait for services to be healthy
4. Test API endpoints
5. Show service status

## 🔧 Development

### Running Services Individually

#### Backend Only

```bash
cd backend
docker build -t ai-receptionist-backend .
docker run -p 8000:8000 --env-file .env ai-receptionist-backend
```

#### Frontend Only

```bash
cd frontend_next
docker build -t ai-receptionist-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 ai-receptionist-frontend
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Stopping Services

```bash
docker-compose down

# Remove volumes (⚠️ deletes data)
docker-compose down -v
```

## 📡 API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### Authentication
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user

### Appointments
- `GET /api/v1/appointments/` - List appointments
- `POST /api/v1/appointments/` - Create appointment
- `GET /api/v1/appointments/{id}` - Get appointment
- `PUT /api/v1/appointments/{id}` - Update appointment
- `DELETE /api/v1/appointments/{id}` - Delete appointment

### Services
- `GET /api/v1/services/` - List services
- `POST /api/v1/services/` - Create service
- `GET /api/v1/services/{id}` - Get service
- `PUT /api/v1/services/{id}` - Update service
- `DELETE /api/v1/services/{id}` - Delete service

### Full API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## 🐛 Troubleshooting

### Backend won't start

1. Check MongoDB is running:
   ```bash
   docker-compose ps mongodb
   ```

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

3. Verify environment variables:
   ```bash
   docker-compose exec backend env | grep MONGO
   ```

### Frontend can't connect to backend

1. Check `NEXT_PUBLIC_API_URL` is set correctly in `docker-compose.yml`
2. Verify backend is accessible:
   ```bash
   curl http://localhost:8000/health
   ```
3. Check frontend logs:
   ```bash
   docker-compose logs frontend
   ```

### MongoDB connection issues

1. Check MongoDB is healthy:
   ```bash
   docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"
   ```

2. Verify MONGO_URI in backend environment:
   ```bash
   docker-compose exec backend env | grep MONGO
   ```

### Port conflicts

If ports 3000, 8000, or 27017 are already in use:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "3001:3000"  # Frontend on 3001
     - "8001:8000"  # Backend on 8001
   ```

## 📦 Production Deployment

### Railway (Backend)

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy from `backend/` directory
4. Use `Dockerfile.railway` or Railway's auto-detection

### Vercel (Frontend)

1. Connect your GitHub repository to Vercel
2. Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
3. Deploy from `frontend_next/` directory

### Environment Variables for Production

**Railway (Backend)**:
- `MONGO_URI` - MongoDB connection string
- `SECRET_KEY` - Strong secret key for JWT
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `FRONTEND_URL` - Your Vercel frontend URL
- `ENVIRONMENT=production`

**Vercel (Frontend)**:
- `NEXT_PUBLIC_API_URL` - Your Railway backend URL: `https://ai-receptionist-production-299a.up.railway.app`

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use strong `SECRET_KEY` in production
- Set `ENVIRONMENT=production` in production
- Configure CORS properly for production domains
- Use HTTPS in production

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

## 📞 Support

[Support Information]

