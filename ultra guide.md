GitHub Copilot Prompt — Ultra-Detailed AI Receptionist Web App for Barber Shop
🎯 Objective

Create a web-based AI receptionist system for a barber shop that:

Answers and chats with clients through Twilio (free tier)

Speaks naturally like a human (using Groq API for the LLM brain)

Books, updates, and deletes appointments

Pushes all data to MongoDB

Provides a React + TailwindCSS dashboard for the barber to manage appointments and see transcripts

Uses Python + FastAPI for all backend logic

No payment system

🧩 Core Flow (End-to-End)

Client calls or sends a message to the Twilio business number.

Twilio Webhook hits FastAPI /webhook route.

FastAPI converts voice→text (if voice) and forwards message to Groq API.

Groq API generates a human-like response according to the conversation state (e.g. greeting, booking flow, cancellation, or general question).

FastAPI sends the response back to the client via Twilio Reply API.

Each message (from client + AI) is stored in MongoDB as a conversation transcript, along with intent and action.

When a booking is confirmed, the appointment data is saved and displayed instantly in the dashboard.

Barber logs into the dashboard to view, edit, or delete any appointment.

🗂 Project Structure (Copilot must generate)
ai_barber_receptionist/
│
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── webhook.py
│   │   ├── appointments.py
│   │   ├── services.py
│   │   └── users.py
│   ├── ai/
│   │   ├── groq_agent.py
│   │   ├── intents.py
│   │   └── conversation_manager.py
│   ├── database/
│   │   └── mongo_config.py
│   ├── models/
│   │   ├── appointment.py
│   │   ├── conversation.py
│   │   └── service.py
│   ├── utils/
│   │   ├── twilio_handler.py
│   │   ├── text_formatter.py
│   │   └── datetime_utils.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/
│   ├── project_plan.md
│   ├── api_endpoints.md
│   ├── database_schema.md
│   ├── architecture_diagram.png
│   └── setup_guide.md
│
└── README.md

⚙️ Backend Stack
Layer	Framework / Tool	Role
Web Server	FastAPI	REST API + Twilio Webhooks
LLM Brain	Groq API	Natural language reasoning
Database	MongoDB	Store appointments, services, and transcripts
Realtime	FastAPI WebSockets	Live updates to dashboard
Environment	python-dotenv	Manage API keys
Voice/SMS Gateway	Twilio (Free Tier)	Handle client communications
🎨 Frontend Stack
Tool	Role
React + Vite	Main UI
TailwindCSS	Styling
Axios	API requests
React Router DOM	Navigation
Socket.io client	Real-time dashboard updates
🧠 AI Conversation Logic
🗣️ Initial Greeting (first response)

When a new client contacts the barber:

Hello there! 👋 This is Ava, the virtual receptionist for Royal Fade Barbershop.  
We specialize in classic cuts, beard trims, and modern styles.  
Would you like to book an appointment, check existing bookings, or learn more about our services?

🤖 Booking Flow

If client says “I’d like to book a haircut”, AI asks:

Name

Preferred date and time

Service type (cut, fade, shave, combo)

Barber preference (optional)

AI confirms:

Perfect, [Name]! I’ve booked you for a [Service] on [Date & Time].  
You’ll receive a confirmation message shortly. Looking forward to seeing you at Royal Fade Barbershop!


Appointment is saved in appointments collection with:

{
  "client_name": "John Doe",
  "service": "Haircut",
  "datetime": "2025-11-14T15:00:00",
  "status": "confirmed",
  "conversation_id": "uuid-123"
}


Transcript entry:

{
  "conversation_id": "uuid-123",
  "messages": [
    {"from": "client", "text": "Hi, can I get a haircut tomorrow?"},
    {"from": "AI", "text": "Sure, what time works for you?"},
    {"from": "client", "text": "3 pm please."},
    {"from": "AI", "text": "Booked! See you tomorrow at 3 pm."}
  ],
  "intent": "book_appointment",
  "completed": true
}

📦 Required Python Dependencies
fastapi
uvicorn
pydantic
pymongo
python-dotenv
requests
twilio
websockets
groq

Frontend Dependencies
react
vite
axios
tailwindcss
react-router-dom
socket.io-client

🧭 Step-by-Step Task Plan (Copilot should follow)
🧱 Step 1 – Environment Setup

Create virtual env, install dependencies.

Configure .env with TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, GROQ_API_KEY, and MONGO_URI.

📞 Step 2 – Twilio Webhook

Add /webhook endpoint to receive SMS or voice calls.

Respond with TwiML for basic greeting.

Store incoming message in MongoDB.

🧠 Step 3 – Groq Integration

Create ai/groq_agent.py to call Groq API.

Generate human-like response using conversation history and barber info (services, hours).

💬 Step 4 – Conversation Memory

Implement conversation_manager.py to track messages and context by phone number.

Automatically branch between booking, update, cancel, or info flows.

🗃️ Step 5 – Database Models

Build MongoDB schemas for appointments, services, and conversations.

CRUD routes for appointments via /appointments API.

🖥️ Step 6 – Frontend Dashboard

Dashboard with:

Appointments List (CRUD)

Conversation Logs / Transcripts

Services Editor (add, edit, delete)

Search Bar / Filters

🔄 Step 7 – Realtime Sync

Use WebSockets so dashboard updates instantly on new bookings or cancellations.

🚀 Step 8 – Deployment

Add Dockerfile + docker-compose for backend + frontend.

Deploy to Render or Railway for free.

💬 Example AI Response Templates
Intent	Example Response
Greeting	“Hi there! I’m Ava, the virtual receptionist at Royal Fade. How can I help you today?”
Booking Confirm	“Got it! I’ve booked your [Service] for [Date & Time]. Anything else?”
Update Booking	“No problem, I’ve moved your appointment to [New Date & Time].”
Cancel	“Your booking has been cancelled. Hope to see you next time!”
Services Info	“We offer haircuts, beard trims, fades, and shaves — all by top-rated barbers.”
🧾 Expected Outcome

A fully functional web app where:

Clients call/text Twilio number.

AI receptionist responds naturally, books, and stores everything.

Barber sees all appointments + conversation transcripts in a live dashboard.

No payment, just scheduling and info.

🧠 Copilot Instructions

Follow the task plan step-by-step; do not code everything at once.

Each step completed must update docs/project_plan.md.

Write clear, commented, production-ready code.

Generate example responses and test data for realism.

Ensure AI replies sound natural, friendly, and context-aware.

Save full transcript of every conversation to MongoDB.

Log final booking summary in both the transcript and the appointments collection.