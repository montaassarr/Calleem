# 🚀 Quick Start Reference Card

## ⚡ 30-Second Start

```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev

# Browser
Open http://localhost:5173
Login: admin@example.com / admin123
```

---

## 📍 All Routes

| Route | Page | Features |
|-------|------|----------|
| `/` | Dashboard | Stats overview |
| `/appointments` | Appointments | **Full CRUD** + table view |
| `/services` | Services | **Full CRUD** + card grid |
| `/conversations` | Conversations | Read-only chat history |
| `/schedule` | Calendar | FullCalendar (week/month/day) |
| `/ai-receptionist` | AI Overview | AI stats & quick actions |
| `/ai-receptionist/test` | AI Chat | Test AI responses |
| `/whatsapp` | WhatsApp | Webhook status |
| `/settings` | Settings Hub | 4 subsections |
| `/settings/business` | Business | Company profile |
| `/settings/team` | Team | **User CRUD** |
| `/settings/ai` | AI Config | Model, prompts |
| `/settings/integrations` | Integrations | API keys |
| `/help` | Help | FAQ & resources |

---

## 🎯 CRUD Operations

### Appointments
- **Create**: Click "New Appointment" → Fill form → Save
- **Edit**: Click pencil icon → Modify → Save
- **Delete**: Click trash icon → Confirm

### Services
- **Create**: Click "New Service" → Fill form → Save
- **Edit**: Click pencil icon → Modify → Save
- **Delete**: Click trash icon → Confirm
- **Toggle**: Use switch to activate/deactivate

### Users (Team)
- **Create**: Settings → Team → "Add Team Member"
- **Edit**: Click pencil icon
- **Delete**: Click trash icon

---

## 🔑 Key Files

### Components
- `AppointmentFormModal.tsx` - Appointment CRUD modal
- `ServiceFormModal.tsx` - Service CRUD modal
- `Sidebar.tsx` - Navigation

### Pages
- `Index.tsx` - Dashboard
- `Appointments.tsx` - Appointments with CRUD
- `Services.tsx` - Services with CRUD
- `Settings/Team.tsx` - User management

### API
- `api/appointments.ts` - appointmentsApi
- `api/services.ts` - servicesApi
- `api/auth.ts` - authApi, usersApi

### Types
- `lib/types.ts` - All TypeScript interfaces

---

## 🛠️ Common Tasks

### Add New Page
1. Create file in `src/pages/YourPage.tsx`
2. Add route in `src/App.tsx`
3. Add nav link in `src/components/Sidebar.tsx`

### Add New API Endpoint
1. Add types in `src/lib/types.ts`
2. Create service in `src/api/yourApi.ts`
3. Export in `src/api/index.ts`
4. Use in component with `useQuery` or `useMutation`

### Fix CORS Error
1. Open `backend/.env`
2. Add `ALLOWED_ORIGINS=http://localhost:5173`
3. Restart backend

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| npm install fails | `rm -rf node_modules package-lock.json && npm install` |
| API 404 errors | Check backend is running on :8000 |
| Login fails | Verify admin created: `python backend/create_admin.py` |
| Calendar blank | Run `npm install @fullcalendar/react` packages |
| Types errors | Check `src/lib/types.ts` matches backend models |

---

## 📦 Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **UI**: Shadcn UI + Tailwind CSS
- **State**: React Query + localStorage
- **Routing**: React Router v6
- **Calendar**: FullCalendar
- **Backend**: FastAPI + MongoDB
- **AI**: Groq (Mixtral-8x7b)
- **Messaging**: Twilio (WhatsApp)

---

## 📚 Documentation

1. **`COMPLETE_SETUP_GUIDE.md`** ⭐ **START HERE** - Full setup instructions
2. **`FINAL_COMPLETION_SUMMARY.md`** - What was built
3. **`BACKEND_FRONTEND_MAPPING.md`** - API reference
4. **`FRONTEND_INTEGRATION_GUIDE.md`** - Patterns & best practices

---

## ✅ Quick Test

```bash
# 1. Check backend
curl http://localhost:8000/health

# 2. Check login
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# 3. Open frontend
# Navigate to http://localhost:5173
# Click around, create appointment, add service
```

---

## 🎊 Success Indicators

✅ Backend running on :8000  
✅ Frontend running on :5173  
✅ Can login with admin credentials  
✅ Dashboard loads stats  
✅ All nav links work (no 404s)  
✅ Can create appointment  
✅ Can create service  
✅ Calendar displays  
✅ No console errors  

---

**Ready to go! 🚀**

_Last updated: January 2025_
