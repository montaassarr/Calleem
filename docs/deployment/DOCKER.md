# AI Receptionist - Docker Quick Start Guide

This guide will help you run the AI Receptionist application using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Start the Application

Simply run:

```bash
./docker-start.sh
```

This script will:
- Check if Docker is running
- Stop any existing containers
- Build the Docker images
- Start all services (MongoDB, Backend, Frontend)
- Wait for all services to be healthy
- Display service URLs and helpful information

### 2. Access the Application

Once started, you can access:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

**Default Login Credentials:**
- Username: `admin`
- Password: `admin123`

### 3. Stop the Application

To stop all services:

```bash
./docker-stop.sh
```

Or manually:

```bash
docker-compose down
```

## Manual Docker Commands

If you prefer to use Docker Compose commands directly:

### Build Images

```bash
docker-compose build
```

### Start Services

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Check Service Status

```bash
docker-compose ps
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
docker-compose down
```

### Remove Everything (including volumes)

```bash
docker-compose down -v
```

## Service Architecture

The application consists of 5 Docker containers:

1. **MongoDB** (Port 27017) - Database
2. **Backend** (Port 8000) - FastAPI application
3. **Frontend** (Port 3000) - Next.js application

## Environment Variables

The application uses environment variables from:
- `.env` (root directory)
- `./backend/.env` (backend-specific variables)

Make sure these files exist before starting the application.

## Troubleshooting

### Services won't start

1. Check if Docker is running:
   ```bash
   docker info
   ```

2. Check logs for errors:
   ```bash
   docker-compose logs
   ```

3. Rebuild images:
   ```bash
   docker-compose build --no-cache
   ```

### Database connection issues

1. Check if MongoDB is healthy:
   ```bash
   docker-compose ps mongodb
   ```

2. View MongoDB logs:
   ```bash
   docker-compose logs mongodb
   ```

### Port conflicts

If ports 3000, 8000, 27017, or 6379 are already in use, you can modify the port mappings in `docker-compose.yml`.

### Reset everything

To completely reset (WARNING: This will delete all data):

```bash
docker-compose down -v
docker system prune -a
./docker-start.sh
```

## Development Mode

For development with hot-reload, you can mount your local code:

1. Edit `docker-compose.yml` to add volume mounts
2. Use development Dockerfiles with hot-reload enabled

## Production Deployment

For production deployment:

1. Update environment variables in `.env`
2. Enable the Nginx reverse proxy in `docker-compose.yml`
3. Configure SSL certificates
4. Use production-ready MongoDB with authentication
5. Set up proper backup strategies

## Health Checks

All services have health checks configured:

- **MongoDB**: Checks database connectivity
- **Backend**: Checks `/health` endpoint
- **Frontend**: Checks if the server responds

You can view health status with:

```bash
docker-compose ps
```

## Useful Commands

```bash
# Enter a running container
docker exec -it ai-receptionist-backend bash
docker exec -it ai-receptionist-frontend sh

# View container resource usage
docker stats

# Clean up unused images
docker image prune

# View all containers (including stopped)
docker ps -a
```

## Support

For issues or questions, please check the main README.md or open an issue on GitHub.
