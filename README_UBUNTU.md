# AI Receptionist - Ubuntu Setup Guide

This guide explains how to run the AI Receptionist on Ubuntu 22.04 using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start (Local Installation)

1.  **Install Dependencies**
    ```bash
    chmod +x install_local.sh
    ./install_local.sh
    ```
    This script will:
    - Check for MongoDB and Redis (and help install them).
    - Set up Python virtual environment and install dependencies.
    - Install Node.js dependencies.
    - Create `.env` from `.env.example`.

2.  **Configure Environment Variables**
    Edit the `.env` file in `backend/.env` and add your API keys:
    ```bash
    nano backend/.env
    ```
    **Required Variables:**
    - `OPENAI_API_KEY`
    - `GROQ_API_KEY`
    - `VAPI_API_KEY`
    - `WHATSAPP_ACCESS_TOKEN`

3.  **Start the Application**
    ```bash
    chmod +x start_local.sh
    ./start_local.sh
    ```
    This will start both Backend (port 8000) and Frontend (port 5173).

## Docker (Optional)

If you prefer Docker, use `setup.sh` instead.

## Management Commands (Makefile)

We have provided a `Makefile` for common tasks:

- `make up`: Start all services in the background.
- `make down`: Stop all services.
- `make logs`: View real-time logs.
- `make shell-backend`: Open a shell inside the backend container (useful for running scripts).
- `make clean`: Stop services and remove volumes (WARNING: Deletes database data).

## Verification

Run the verification script to check system health:
```bash
python3 verify_setup.py
```

## Data Migration (Windows to Ubuntu)

If you have existing data on Windows, you can migrate it using `mongodump` and `mongorestore`:

1.  **On Windows**:
    ```powershell
    mongodump --uri="mongodb://localhost:27017/ai_barber_receptionist" --out="C:\backup"
    ```
    Copy the `backup` folder to your Ubuntu machine.

2.  **On Ubuntu**:
    ```bash
    # Copy backup to container
    docker cp backup/ai_barber_receptionist ai-receptionist-mongodb:/tmp/dump

    # Restore inside container
    docker compose exec mongodb mongorestore --uri="mongodb://localhost:27017/ai_barber_receptionist" /tmp/dump
    ```

## Troubleshooting

- **MongoDB Connection Failed**: Check if the `mongodb` container is healthy: `docker compose ps`.
- **Frontend API Error**: Ensure `VITE_API_URL` is correct in `docker-compose.yml` (default: `http://localhost:8000/api/v1`).
- **Permission Denied**: Run `chmod +x setup.sh` and `chmod +x backend/start.sh`.

## Project Structure

- `backend/`: FastAPI application.
- `frontend/`: React/Vite application.
- `docker-compose.yml`: Docker services configuration.
- `setup.sh`: Automated setup script.
