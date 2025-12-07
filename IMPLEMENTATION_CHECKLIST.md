Manual Service Startup Guide
Use this guide to start the CallFlow AI components manually in separate terminals. This is useful for development and debugging.

IMPORTANT

Ensure you have 4 separate terminals open.

1. MongoDB (Database)
Ensure MongoDB is running as a system service.

sudo systemctl start mongod
sudo systemctl status mongod
If it's already active (green), you don't need to do anything.

2. Backend (FastAPI)
This handles the API, Authorization, and AI Agent logic. Terminal 1:

cd backend
source venv/bin/activate  # If using virtualenv
# OR just run if dependencies are global/user
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Wait until you see: Application startup complete.

3. Frontend (Next.js Dashboard)
The admin dashboard for tenants. Terminal 2:

cd frontend_next
npm run dev
Access at: http://localhost:3000

4. LiveKit Agent (Voice Worker)
The Python worker that handles real-time voice conversations. Terminal 3:

cd livekit-agent-worker
source venv/bin/activate # If using virtualenv
python3 agent.py dev
Wait until you see: Connecting to signal connection and Connected to signal connection

5. Ngrok (Optional / External Access)
If you need to expose your local backend to the internet (e.g., for external webhooks or WhatsApp), use ngrok. Terminal 4:

ngrok http 8000