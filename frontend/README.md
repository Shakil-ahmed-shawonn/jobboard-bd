# JobBoard BD — Frontend

React + Vite + Tailwind v4. Role-based dashboards for Employer and Job Seeker.

## Local setup
```bash
npm install
npm run dev
```
Open http://localhost:5173 — API calls to `/api/*` are proxied to `http://127.0.0.1:8000` (the Django backend). Start the backend first.

## Structure
- `src/api/client.js` — axios instance; attaches JWT, auto-refreshes on 401
- `src/context/AuthContext.jsx` — login/register/logout, role fetched from `/api/accounts/me/`
- `src/components/ProtectedRoute.jsx` — redirects by auth + role
- `src/pages/employer/` — PostJob, Dashboard (applicants sorted by AI fit score)
- `src/pages/seeker/` — Browse (search + apply with resume upload), MyApplications

## Build for deployment
```bash
npm run build   # outputs dist/
```
Deploy `dist/` to Netlify (import from GitHub, per established workflow — Vercel is blocked for BD phone numbers).

**Before deploying:** set the production API base URL. Currently `client.js` uses a relative `/api` baseURL, which only works via the Vite dev proxy. For production, either:
1. Serve frontend and backend from the same domain (reverse proxy `/api` → Django), or
2. Set `baseURL: import.meta.env.VITE_API_URL` in `client.js` and add `VITE_API_URL=https://your-backend.onrender.com/api` to Netlify's environment variables.

## Troubleshooting
| Error | Fix |
|---|---|
| Network error on every request | Backend not running, or wrong proxy target in `vite.config.js` |
| Stuck redirect loop between `/login` and `/` | Corrupt `localStorage` — clear it (`localStorage.clear()` in devtools console) |
| 401 immediately after login | Backend `SIMPLE_JWT` clock skew or `ANTHROPIC_API_KEY`/DB misconfigured causing `/me/` to fail — check backend logs |
| File upload fails silently | Confirm `Content-Type: multipart/form-data` header is set (already handled in `Browse.jsx`) and file is under 5MB |
| Tailwind classes not applying | Confirm `@import "tailwindcss";` is the first line of `index.css` and `postcss.config.js` uses `@tailwindcss/postcss`, not the old `tailwindcss` plugin key (v4 breaking change) |
