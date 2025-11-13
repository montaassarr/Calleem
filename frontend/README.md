# React + Vite — AI Receptionist frontend

This is a small Vite + React 18 scaffold that serves as the admin/dashboard for the AI Receptionist barber-shop project.

It is intentionally minimal and wired to the backend API at runtime. The frontend reads the API base URL from the environment variable VITE_API_BASE (for example: `http://localhost:8000/api/v1`). If not set, the client falls back to `http://localhost:8000/api/v1`.

## Prerequisites

- Node.js >= 18 (recommended)
- npm (or yarn / pnpm)

## Quick start

1. Install dependencies

   ```bash
   npm install
   ```

2. (Optional) Create a local env file to override the API base

   ```bash
   # .env.local
   VITE_API_BASE=http://localhost:8000/api/v1
   ```

3. Start the dev server (HMR enabled)

   ```bash
   npm run dev
   ```

4. Open the URL shown by Vite (usually http://localhost:5173)

## Build & preview

- Build production assets:

  ```bash
  npm run build
  ```

- Preview the production build locally:

  ```bash
  npm run preview
  ```

## How the frontend talks to the backend

- The axios client is in `src/lib/api.js` and reads `import.meta.env.VITE_API_BASE` at runtime. Ensure your backend is running and reachable at the configured address.

## Auth & protected routes

- This scaffold uses a simple JWT-in-localStorage approach for demo purposes. Tokens are stored in localStorage and attached to API requests by `src/lib/api.js`. For production, consider a secure refresh-token flow and httpOnly cookies.

## Next steps / recommended improvements

- Add Tailwind CSS or a component library for styling.
- Implement appointment create/edit forms using a robust date/time picker (respect backend TIMEZONE setting).
- Add client-side validation and nicer error handling for API responses.
- Add E2E tests (Playwright or Cypress) and CI build steps.

## Troubleshooting

- If API calls fail, open the browser devtools Network tab and verify the request URL. Confirm `VITE_API_BASE` is correct and the backend server is running.

## Running the backend locally (reminder)

- From the `backend/` directory start the FastAPI server:

  ```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

If you want me to add Tailwind, protected-route components, or implement the appointment UI next, tell me which piece to build first and I'll continue.
