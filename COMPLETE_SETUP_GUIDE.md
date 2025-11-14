# 🎯 Complete Frontend Setup & Run Guide

## 📋 Overview

This guide covers the complete setup, run, and testing procedures for the AI Receptionist Dashboard frontend application.

---

## 🚀 Quick Start (TL;DR)

```bash
# Frontend Setup
cd frontend
npm install
npm run dev

# Backend Setup (Separate Terminal)
cd backend
pip install -r requirements.txt
python main.py

# Access Application
Frontend: http://localhost:5173
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 📦 Prerequisites

### Required Software
- **Node.js**: v18+ (includes npm)
- **Python**: 3.9+
- **MongoDB**: 6.0+ (running locally or cloud)
- **Git**: For version control

### Verify Installations
```bash
node --version   # Should be v18+
npm --version    # Should be 9+
python --version # Should be 3.9+
mongod --version # Should be 6.0+
```

---

## 🛠️ Backend Setup

### 1. Navigate to Backend Directory
```bash
cd /home/montassar/Desktop/ai_receptionist/backend
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend` directory:

```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_receptionist

# Twilio (WhatsApp Integration)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=REDACTED
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_VERIFY_SID=your_verify_sid

# Groq AI
GROQ_API_KEY=REDACTED

# JWT Authentication
SECRET_KEY=REDACTED
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. Initialize Database (First Time Only)
```bash
# Create admin user
python create_admin.py

# This creates:
# Email: admin@example.com
# Password: admin123
```

### 6. Start Backend Server
```bash
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 💻 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd /home/montassar/Desktop/ai_receptionist/frontend
```

### 2. Install Node Dependencies
```bash
npm install
```

**This installs:**
- React 18 + TypeScript
- Vite (build tool)
- React Router (routing)
- TanStack Query (data fetching)
- Shadcn UI components
- Tailwind CSS
- FullCalendar (schedule view)
- Axios (HTTP client)
- And more...

### 3. Verify package.json Scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

### 4. Start Development Server
```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 5. Open Browser
Navigate to: **http://localhost:5173**

---

## 🔐 First Login

### Default Admin Credentials
```
Email:    admin@example.com
Password: admin123
```

**⚠️ IMPORTANT:** Change admin password after first login via Settings → Team → Edit admin user.

---

## 📱 Application Routes

### Public Routes
- `/login` - Authentication page

### Protected Routes (Require Login)

#### Main Navigation
- `/` - Dashboard (stats overview)
- `/appointments` - Appointments management
- `/conversations` - Conversation history
- `/services` - Service management
- `/schedule` - Calendar view (FullCalendar)
- `/ai-receptionist` - AI stats & overview
- `/ai-receptionist/test` - AI chat simulator
- `/whatsapp` - WhatsApp webhook status

#### Settings
- `/settings` - Settings hub
- `/settings/business` - Business profile
- `/settings/team` - Team members (user CRUD)
- `/settings/ai` - AI configuration (model, prompts)
- `/settings/integrations` - API keys (Groq, Twilio)

#### Help
- `/help` - Help & FAQ

---

## 🧪 Testing the Application

### 1. Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

**Expected:** JSON response with `access_token`

### 2. Test Services API
```bash
# Get all services
curl http://localhost:8000/api/v1/services \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Test Frontend Pages
1. **Login Page**: Enter credentials → should redirect to dashboard
2. **Dashboard**: Should load stats (appointments, conversations, services)
3. **Appointments**: Click "New Appointment" → modal opens → fill form → save
4. **Services**: Toggle active/inactive switch → status updates
5. **Schedule**: View calendar → events show appointments
6. **Settings → Team**: Add new team member → appears in table
7. **AI Test**: Send test message → AI responds (requires Groq API key)

---

## 🎨 Key Features Implemented

### ✅ Complete CRUD Operations
- **Appointments**: Create, read, update, delete with modal forms
- **Services**: Create, read, update, delete with modal forms
- **Team Members**: Create, read, update, delete (in Settings → Team)
- **Conversations**: Read-only list with search & filters

### ✅ Advanced UI Components
- **Glass-morphism Design**: Backdrop blur, gradients, transparency
- **Responsive Layout**: Works on desktop, tablet, mobile
- **Loading States**: Spinners while fetching data
- **Error Handling**: Toast notifications for success/error
- **Modal Dialogs**: Shadcn Dialog for forms
- **Confirmation Dialogs**: AlertDialog for delete confirmations
- **Data Tables**: Sortable, searchable tables
- **Calendar View**: FullCalendar with week/month/day views

### ✅ Real-time Features
- **React Query**: Automatic cache invalidation and refetching
- **Optimistic Updates**: UI updates before server confirms
- **Background Refetch**: Data stays fresh automatically

### ✅ Settings Management
- **Business Profile**: Company details, hours, timezone
- **Team Members**: User management with roles
- **AI Configuration**: Model selection, temperature, prompts
- **Integrations**: Groq & Twilio API keys

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   ├── DashboardHeader.tsx
│   │   ├── AppointmentFormModal.tsx  # NEW
│   │   ├── ServiceFormModal.tsx      # NEW
│   │   ├── LoadingSpinner.tsx
│   │   ├── Modal.tsx
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/               # Page components
│   │   ├── Index.tsx        # Dashboard
│   │   ├── Login.tsx
│   │   ├── Appointments.tsx # UPDATED with CRUD
│   │   ├── Conversations.tsx
│   │   ├── Services.tsx     # UPDATED with CRUD
│   │   ├── Schedule.tsx     # FullCalendar
│   │   ├── Help.tsx
│   │   ├── AIReceptionist/
│   │   │   ├── Index.tsx    # AI overview
│   │   │   └── Test.tsx     # AI chat simulator
│   │   └── Settings/
│   │       ├── Index.tsx    # Settings hub
│   │       ├── Business.tsx
│   │       ├── Team.tsx     # User CRUD
│   │       ├── AI.tsx       # AI config
│   │       └── Integrations.tsx
│   ├── lib/
│   │   ├── types.ts         # TypeScript interfaces (46 types)
│   │   └── api.js           # API base config
│   ├── api/                 # API service layer
│   │   ├── auth.ts          # authApi, usersApi
│   │   ├── appointments.ts  # appointmentsApi
│   │   ├── conversations.ts # conversationsApi
│   │   ├── services.ts      # servicesApi
│   │   ├── webhook.ts       # webhookApi
│   │   └── index.ts         # Centralized exports
│   ├── App.tsx              # UPDATED with all routes
│   ├── main.tsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── tsconfig.json
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# OR use a different port
uvicorn main:app --reload --port 8001
```

#### MongoDB Connection Error
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Check connection
mongosh --eval "db.runCommand({ ping: 1 })"
```

#### ImportError: No module named 'X'
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

#### npm install fails
```bash
# Clear cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### "Cannot find module" errors
```bash
# Ensure all dependencies are installed
npm install

# Check for TypeScript errors
npm run build
```

#### API calls fail with CORS errors
- Check `ALLOWED_ORIGINS` in backend `.env`
- Ensure it includes `http://localhost:5173`
- Restart backend server after changing `.env`

#### FullCalendar not displaying
```bash
# Verify FullCalendar packages
npm list @fullcalendar/react

# Reinstall if missing
npm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
```

---

## 🔄 Development Workflow

### Making Changes

1. **Edit Code**: Make changes in `src/` directory
2. **Auto-Reload**: Vite hot-reloads changes automatically
3. **Test**: Verify changes in browser at http://localhost:5173
4. **Commit**: Git add/commit/push changes

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add nav link in `src/components/Sidebar.tsx` (if needed)
4. Create API service in `src/api/` (if needed)

### Adding New API Endpoints

1. Update TypeScript types in `src/lib/types.ts`
2. Create/update API service in `src/api/`
3. Use React Query `useQuery` or `useMutation` in components

---

## 📦 Building for Production

### Build Frontend
```bash
cd frontend
npm run build
```

Output: `frontend/dist/` directory

### Build Docker Containers
```bash
# From project root
docker-compose up --build
```

### Deploy
- Frontend: Serve `dist/` with Nginx, Vercel, Netlify, etc.
- Backend: Deploy FastAPI with Gunicorn/Uvicorn on server
- Database: Use MongoDB Atlas for cloud database

---

## 📊 API Documentation

### Swagger UI
Access interactive API docs at: **http://localhost:8000/docs**

### API Endpoints

#### Authentication
- `POST /api/v1/users/login` - Login (get token)
- `POST /api/v1/users/register` - Register new user
- `GET /api/v1/users/me` - Get current user

#### Users
- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

#### Appointments
- `GET /api/v1/appointments` - List appointments
- `POST /api/v1/appointments` - Create appointment
- `GET /api/v1/appointments/{id}` - Get appointment
- `PUT /api/v1/appointments/{id}` - Update appointment
- `DELETE /api/v1/appointments/{id}` - Delete appointment

#### Services
- `GET /api/v1/services` - List services
- `POST /api/v1/services` - Create service
- `GET /api/v1/services/{id}` - Get service
- `PUT /api/v1/services/{id}` - Update service
- `DELETE /api/v1/services/{id}` - Delete service
- `PATCH /api/v1/services/{id}/toggle` - Toggle active status

#### Conversations
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation
- `GET /api/v1/conversations/search` - Search by phone

#### Webhook
- `GET /api/v1/webhook/status` - Get webhook status
- `POST /api/v1/webhook` - Twilio webhook endpoint

---

## 🎓 Next Steps

### 1. Customize Branding
- Update logo in `frontend/public/`
- Change colors in `tailwind.config.js`
- Modify business name in Settings → Business

### 2. Configure Integrations
- Add Groq API key in Settings → Integrations
- Add Twilio credentials for WhatsApp
- Test AI receptionist in AI Receptionist → Test

### 3. Add Services
- Go to Services page
- Click "New Service"
- Add your business services (e.g., "Haircut", "Consultation")

### 4. Set Business Hours
- Go to Settings → Business
- Configure operating hours
- Set timezone

### 5. Invite Team Members
- Go to Settings → Team
- Click "Add Team Member"
- Assign roles (admin, staff, receptionist)

---

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Shadcn UI Components](https://ui.shadcn.com)
- [FullCalendar Docs](https://fullcalendar.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MongoDB Manual](https://docs.mongodb.com/manual/)

---

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs (in terminal running python main.py)
# Frontend logs (browser console: F12)

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Docker logs
docker-compose logs -f
```

### Common Issues
- **404 Errors**: Check routes in `App.tsx`
- **API Errors**: Check backend logs and API docs
- **Data Not Loading**: Check React Query DevTools in browser
- **Styling Issues**: Check Tailwind classes and `index.css`

---

## ✅ Completion Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] MongoDB connected successfully
- [ ] Admin user created and can login
- [ ] Dashboard loads with stats
- [ ] Can create appointments
- [ ] Can create services
- [ ] Can add team members
- [ ] Calendar displays appointments
- [ ] AI test page accessible
- [ ] Settings pages functional
- [ ] All navigation links work
- [ ] No console errors in browser
- [ ] API endpoints respond correctly

---

**🎉 You're all set! The AI Receptionist Dashboard is ready to use.**
