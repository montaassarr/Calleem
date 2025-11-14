# 🚀 Quick Reference Card

## Login Credentials
```
Username: admin
Password: admin123
```

## Start Commands

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
# Runs on http://localhost:8080
```

### Database
```bash
# MongoDB should be running
sudo systemctl status mongod
```

---

## API Endpoints Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Quick Test with curl
```bash
# Login
curl -X POST http://localhost:8000/api/v1/users/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Get appointments (with token)
curl http://localhost:8000/api/v1/appointments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Frontend Routes

| URL | Page | Status |
|-----|------|--------|
| `/login` | Login | ✅ Working |
| `/` | Dashboard | ✅ Working |
| `/appointments` | Appointments List | ✅ Working |
| `/conversations` | Conversations | ✅ Working |
| `/services` | Services | ✅ Working |
| `/ai-receptionist/test` | AI Chat Test | ✅ Working |
| `/whatsapp` | Twilio Integration | ✅ Working |

---

## API Service Imports

```typescript
// Import all services
import {
  authApi,
  usersApi,
  appointmentsApi,
  conversationsApi,
  servicesApi,
  webhookApi
} from "@/api";

// Use in components
const { data } = useQuery({
  queryKey: ["appointments"],
  queryFn: () => appointmentsApi.list(),
});
```

---

## Common Tasks

### Create a new page
1. Create `frontend/src/pages/YourPage.tsx`
2. Add route in `App.tsx`:
```tsx
<Route path="/your-page" element={
  <ProtectedRoute>
    <YourPage />
  </ProtectedRoute>
} />
```
3. Add to sidebar in `Sidebar.tsx`

### Add new API endpoint
1. Add function to appropriate file in `src/api/`
2. Define types in `src/lib/types.ts`
3. Use in component with React Query

### Create a form
1. Use Shadcn UI form components
2. Call API service on submit
3. Use `useMutation` for POST/PUT/DELETE

---

## File Structure

```
frontend/src/
├── api/              # API service layer
│   ├── auth.ts
│   ├── appointments.ts
│   ├── conversations.ts
│   ├── services.ts
│   ├── webhook.ts
│   └── index.ts
├── components/       # Reusable components
│   ├── Sidebar.tsx
│   ├── DashboardHeader.tsx
│   └── ui/          # Shadcn components
├── lib/
│   ├── api.ts       # Axios instance
│   ├── types.ts     # TypeScript types
│   └── utils.ts
├── pages/           # Route pages
│   ├── Index.tsx
│   ├── Login.tsx
│   ├── Appointments.tsx
│   ├── Conversations.tsx
│   ├── Services.tsx
│   ├── WhatsApp.tsx
│   └── AIReceptionist/
│       └── Test.tsx
└── App.tsx          # Router config
```

---

## Environment Variables

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend `.env`
```env
MONGO_URI=mongodb://localhost:27017
GROQ_API_KEY=REDACTED
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=REDACTED
CORS_ORIGINS=["http://localhost:8080",...]
```

---

## Debugging

### Check API is running
```bash
curl http://localhost:8000/health
```

### Check frontend can reach backend
Open browser console → Network tab → Check requests to `/api/v1`

### Clear React Query cache
In browser console:
```javascript
localStorage.clear()
// Then refresh page
```

### Check MongoDB
```bash
mongosh
> use ai_barber_receptionist
> db.appointments.find()
> db.conversations.find()
```

---

## Next Steps (Optional)

1. **Build appointment create modal** - Use Shadcn Dialog + Form
2. **Add calendar view** - Install FullCalendar or similar
3. **Build settings pages** - Business profile, team members
4. **Add real-time updates** - WebSocket integration

---

## Support

- **Backend API Docs**: http://localhost:8000/docs
- **Documentation**: See `docs/` folder
- **Type Definitions**: `frontend/src/lib/types.ts`
- **API Services**: `frontend/src/api/`

---

**Everything is ready to use!** 🎉
