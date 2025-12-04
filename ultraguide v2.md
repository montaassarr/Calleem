GitHub Copilot Prompt — “AI Receptionist Barber Web App (with stack_components file)”

🧩 Goal:
You are my coding assistant. Your mission is to build a full AI-powered receptionist web app for a barber shop using Python and open-source frameworks.
The app will let clients chat (text or voice) via a Twilio free tier phone number, handled by an AI receptionist that talks like a human, books appointments, updates or cancels them, and syncs all information with a web dashboard for the barber team.

You will create:

The full working web app project structure.

A separate file named stack_components.txt listing and installing all required frameworks, libraries, APIs, open-source tools, and environment variables, organized by layer.

A step-by-step documentation file (project_doc.md) to guide your next tasks and commands sequentially — one phase at a time.

⚙️ Project Features

Main idea:
An AI receptionist answers clients’ Twilio calls or messages, responds in human-like text, manages booking requests, updates and deletes appointments, and stores everything in a connected database (MongoDB or PostgreSQL).

System flow:

A client texts or calls the barber’s Twilio number.

The AI receptionist responds naturally (like a human assistant) using an LLM (Groq API).

The AI confirms the client’s identity or asks for missing info (name, date, time, preferred barber, etc).

The AI creates, updates, or deletes the booking in the database.

The barber team dashboard updates in real time.

A full transcript of the conversation is saved and displayed on the dashboard.

💻 Tech Stack Instructions

Backend (Python):

Use FastAPI or Flask (choose the most scalable one).

Integrate Twilio API for phone/text communication (free tier).

Integrate Groq API (for LLM text generation).

Add SQLAlchemy or PyMongo (depending on database choice).

Use Pydantic for data validation.

Use Celery + Redis for background task handling if needed.

Add dotenv for environment variable management.

Implement JWT or session-based authentication for admin login.

Frontend (Web dashboard):

Use React.js + TailwindCSS (modern responsive UI).

Add Framer Motion for animations.

Include a chat view that shows AI-client conversation.

Add an appointments view with CRUD (create, read, update, delete).

Include a statistics panel (e.g., number of bookings, busiest times).

AI Layer:

LLM = Groq API (or fallback to Hugging Face free model).

Create a Prompt Template System for dynamic responses.

Store transcripts in the database.

Database:

Use MongoDB Atlas or PostgreSQL.

Define collections/tables for:

Clients

Appointments

Conversations

Admins

🗂️ Files to Create Automatically

main.py → Entry point for FastAPI backend

ai_agent/ → Folder for AI logic

conversation_handler.py

booking_manager.py

prompt_templates.py

database/ →

models.py

db_config.py

routes/ →

client_routes.py

admin_routes.py

twilio_webhook.py

frontend/ → React app with:

Dashboard.jsx

ChatView.jsx

Bookings.jsx

stack_components.txt → List + install commands for all frameworks, tools, APIs

project_doc.md → Step-by-step documentation and next tasks

.env.example → Example of environment variables

🧩 In stack_components.txt, include:

List all dependencies grouped by layer:

AI Layer

groq

transformers

langchain

openai (fallback)

torch

sentencepiece

Backend Layer

fastapi

uvicorn

twilio

pydantic

python-dotenv

requests

aiohttp

Database Layer

pymongo (for MongoDB)

OR sqlalchemy + psycopg2 (for PostgreSQL)

Frontend Layer

react

vite

tailwindcss

framer-motion

axios

DevOps / Tools

docker

docker-compose

nginx

gunicorn

redis + celery

🧠 AI Receptionist Example Behavior

When a new client texts the barber shop:

Client: Hi, I want to book an appointment for tomorrow.
AI Receptionist: Sure! Can I get your full name and the service you’d like?
Client: Name’s Karim, I’d like a haircut at 3PM.
AI Receptionist: Great, Karim! I’ve booked you for a haircut tomorrow at 3PM. You’ll receive a confirmation shortly.


✅ The AI stores this conversation in conversations
✅ Creates a booking record in the database
✅ Updates the admin dashboard
✅ Generates a transcript summary like:

📋 Appointment Summary:
- Name: Karim
- Service: Haircut
- Date: Tomorrow
- Time: 3PM
- Status: Confirmed

🔧 Final Step for Copilot

Tell Copilot:

“Now generate the full initial project structure with all files and directories.
Then populate stack_components.txt with all framework install commands and layer documentation.
After that, follow the project_doc.md to complete the implementation step-by-step.