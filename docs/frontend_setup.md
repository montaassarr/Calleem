# AI Receptionist Frontend Setup Guide

## Overview

This is the React-based admin dashboard for the AI Receptionist system. It provides a user-friendly interface for managing appointments, viewing conversations, managing services, and monitoring system performance.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Day.js** - Date/time manipulation

## Prerequisites

- Node.js >= 18.x
- npm or yarn
- Backend API running (see backend setup guide)

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env.local` file:

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```bash
VITE_API_BASE=http://localhost:8000/api/v1
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (Vite's default port).

## Available Scripts

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run linter
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Navbar.jsx      # Top navigation bar
│   │   ├── Modal.jsx       # Modal dialog
│   │   ├── ProtectedRoute.jsx  # Auth wrapper
│   │   └── LoadingSpinner.jsx  # Loading indicator
│   ├── pages/              # Page components
│   │   ├── Login.jsx       # Login/Register page
│   │   ├── Dashboard.jsx   # Main dashboard
│   │   ├── Appointments.jsx    # Appointment management
│   │   ├── Conversations.jsx   # Chat history viewer
│   │   └── Services.jsx    # Services CRUD
│   ├── lib/
│   │   └── api.js          # Axios client configuration
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles (Tailwind)
├── public/                 # Static assets
├── .env.example            # Environment template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── postcss.config.js       # PostCSS configuration
```

## Features

### Authentication
- Login/Register pages
- JWT token storage in localStorage
- Protected routes (redirect to login if not authenticated)
- Logout functionality

### Dashboard
- Overview statistics (total, confirmed, pending, cancelled appointments)
- Today's appointments list
- Quick action cards

### Appointments
- View all appointments in a table
- Filter by status (all, pending, confirmed, completed, cancelled)
- Create new appointments
- Edit existing appointments
- Delete appointments
- Date/time picker for scheduling

### Conversations
- View all customer conversations
- Search by phone number or message content
- View conversation details and message history
- Real-time message display with role indicators (customer/AI)
- Conversation metadata (state, timestamps)

### Services
- View all services in a grid layout
- Add new services
- Edit existing services (name, description, price, duration)
- Delete services
- Toggle active/inactive status
- Visual indicators for service status

## API Integration

The frontend communicates with the backend API using Axios. The API client is configured in `src/lib/api.js`:

```javascript
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

## Styling with Tailwind

Tailwind CSS is configured with default settings. Key utilities used:

- **Layout**: `flex`, `grid`, `space-x-*`, `space-y-*`
- **Spacing**: `p-*`, `m-*`, `px-*`, `py-*`
- **Colors**: `bg-blue-600`, `text-gray-900`, etc.
- **Responsive**: `sm:`, `md:`, `lg:` breakpoints
- **States**: `hover:`, `focus:`, `disabled:`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE` | Backend API base URL | `http://localhost:8000/api/v1` |

## Production Build

### Build the application

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Preview production build

```bash
npm run preview
```

### Deploy

The `dist/` folder can be deployed to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Your own nginx/Apache server

### Example nginx configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (optional - if backend is on same server)
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### CORS Issues

If you see CORS errors in the browser console:

1. Make sure backend CORS_ORIGINS includes your frontend URL
2. Check `backend/.env`:
   ```
   CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
   ```

### API Connection Failed

1. Verify backend is running: `http://localhost:8000/api/v1/health`
2. Check VITE_API_BASE in `.env.local`
3. Open browser DevTools Network tab to inspect failed requests

### Authentication Issues

1. Check localStorage for `access_token`
2. Verify token format (should be a JWT string)
3. Check backend logs for authentication errors
4. Try logging out and logging back in

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to components will reflect immediately without full page reload.

### Debugging

- Use React DevTools browser extension
- Use `console.log()` for quick debugging
- Check Network tab in DevTools for API calls
- Use VS Code debugger with Chrome

### Adding New Pages

1. Create component in `src/pages/NewPage.jsx`
2. Add route in `src/App.jsx`:
   ```jsx
   <Route path="/newpage" element={
     <ProtectedRoute>
       <NewPage />
     </ProtectedRoute>
   } />
   ```
3. Add navigation link in `src/components/Navbar.jsx`

### Adding New API Endpoints

Use the `api` client from `src/lib/api.js`:

```javascript
import api from '../lib/api'

// GET request
const data = await api.get('/endpoint')

// POST request
await api.post('/endpoint', { key: 'value' })

// PUT request
await api.put('/endpoint/123', { key: 'value' })

// DELETE request
await api.delete('/endpoint/123')
```

## Security Considerations

### Current Implementation (Development)

- JWT tokens stored in localStorage
- Simple token-based authentication
- No refresh token mechanism

### Production Recommendations

1. **Use httpOnly cookies** instead of localStorage for tokens
2. **Implement refresh tokens** for better security
3. **Add CSRF protection** for state-changing operations
4. **Enable HTTPS** for all production deployments
5. **Implement rate limiting** on login endpoints
6. **Add session timeout** and auto-logout
7. **Sanitize user inputs** to prevent XSS

## Performance Optimization

### Code Splitting

Vite automatically code-splits routes. Consider additional splitting for large components:

```javascript
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('./HeavyComponent'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### Image Optimization

- Use WebP format for images
- Compress images before upload
- Consider lazy loading for images below the fold

### Bundle Size

Check bundle size:

```bash
npm run build
```

Analyze bundle (install plugin):

```bash
npm install -D rollup-plugin-visualizer
```

## Testing (To Be Implemented)

### Unit Tests (Vitest)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

### E2E Tests (Playwright)

```bash
npm install -D @playwright/test
```

## Next Steps

1. Add real-time updates with WebSockets
2. Implement notification system
3. Add calendar view for appointments
4. Create analytics/reporting dashboard
5. Add export functionality (CSV/PDF)
6. Implement user preferences/settings
7. Add multi-language support
8. Create mobile-responsive improvements

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Check browser console for errors
- Review API documentation: `docs/api_endpoints.md`
- Check backend health: `http://localhost:8000/api/v1/health`

## License

This project is part of the AI Receptionist system. See main README.md for license information.
