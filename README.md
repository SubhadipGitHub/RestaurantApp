# 🍽️ Restaurant Table Booking App

A full-stack table-booking app: sign in with Google, view a restaurant's tables,
and book one. FastAPI backend, Next.js frontend, MongoDB Atlas for storage.

## ✨ Features

- **Google sign-in** with a server-verified, HttpOnly session cookie.
- **Live table layout** showing seat counts and availability.
- **Booking** with an atomic table claim, so two people cannot take the same
  table at once.
- **Bookings are tied to the signed-in user** — identity comes from the session,
  never from the request body.

## 🛠️ Tech stack

**Frontend** — Next.js 15 (App Router), React 18, Tailwind CSS 3
**Backend** — FastAPI, Motor (async MongoDB), python-jose
**Data** — MongoDB Atlas
**Hosting** — Vercel (frontend) + Render (backend)

## 📂 Project structure

```
.
├── Backend/                     # FastAPI service
│   ├── main.py                  # Routes: auth, bookings, tables
│   ├── auth.py                  # Session tokens + the auth dependency
│   ├── config.py                # Env loading with fail-fast validation
│   ├── seed.py                  # Create a restaurant's initial tables
│   ├── smoke_test.py            # Offline auth/hardening checks
│   ├── Dockerfile
│   └── requirements.txt
├── Frontend/restaurant-frontend/   # Next.js app (note: one level deep)
│   ├── next.config.mjs          # Same-origin rewrite to the backend
│   └── src/
│       ├── app/                 # Routes: /, /login, /dashboard, /customer
│       │   └── AuthContext.js   # Auth state, sourced from GET /me
│       └── components/          # AppShell, TableSelection, Table
├── render.yaml                  # Render Blueprint for the backend
└── DEPLOYMENT.md                # Full deployment runbook
```

## 🏗️ Architecture

The browser only ever talks to the frontend origin. Next.js rewrites
`/api/backend/*` through to the FastAPI service, which removes CORS from the
picture and keeps the session cookie first-party.

```
Browser ──► Next.js (Vercel) ──rewrite──► FastAPI (Render) ──► MongoDB Atlas
```

Sign-in flow:

1. The user hits `/api/backend/login/google`; the backend mints an OAuth `state`
   and redirects to Google.
2. Google returns to `/api/backend/auth/google`, which verifies `state`,
   exchanges the code, and upserts the user.
3. The backend issues **its own** JWT as an `HttpOnly; Secure; SameSite=Lax`
   cookie and redirects to `/dashboard`. No token ever appears in a URL.

## 🚀 Getting started

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for the full runbook — MongoDB Atlas
setup, the Google OAuth client, and deploying both services.

Local development in short:

```bash
# Backend
cd Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in; set COOKIE_SECURE=false for local HTTP
uvicorn main:app --reload --port 8000

# Frontend, in another shell
cd Frontend/restaurant-frontend
npm install
cp .env.example .env.local
npm run dev                   # http://localhost:3000
```

Then seed some tables: `python Backend/seed.py --restaurant-id REST_001 --count 6`

## 🔌 API

All paths are reachable from the frontend as `/api/backend/...`.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | — | Liveness probe |
| `GET` | `/login/google` | — | Redirect to Google's consent screen |
| `GET` | `/auth/google` | — | OAuth callback; sets the session cookie |
| `GET` | `/me` | ✅ | The signed-in user |
| `POST` | `/logout` | — | Clear the session cookie |
| `GET` | `/tables?restaurant_id=` | — | List a restaurant's tables |
| `POST` | `/tables` | ✅ | Create a table |
| `PUT` | `/update_table/{id}` | ✅ | Change status or seat count |
| `GET` | `/bookings` | ✅ | The caller's own bookings |
| `POST` | `/bookings` | ✅ | Book a table |
| `PUT` | `/bookings/{id}` | ✅ | Update a booking |
| `PUT` | `/clear_table_booking/{id}` | ✅ | Cancel and release the table |

Interactive docs are available at `/docs` when `ENABLE_DOCS=true`. They are off
by default, since they enumerate every mutation endpoint.

## 🗃️ Data model

**users** — `_id` (`USER_<hex>`), `email`, `name`, `picture`, `created_at`, `last_login`

**tables** — `_id` (`TABLE_<hex>`), `restaurant_id`, `label`, `seats`,
`status` (`AVAILABLE` | `BLOCKED` | `OCCUPIED`), `booking_id`

**bookings** — `_id` (`BOOKING_<hex>`), `restaurant_id`, `table_id`,
`no_of_people`, `time_slot`, `customer_name`, `customer_email`,
`status` (`PENDING` | `CONFIRMED` | `CANCELLED`)

## ⚠️ Known limitations

- **Availability ignores `time_slot`.** A booked table stays `OCCUPIED` until
  explicitly released, so it is a "claimed until released" model rather than a
  time-slotted one. Real interval-based availability is the top follow-up.
- **Test coverage** is limited to `Backend/smoke_test.py`, which checks auth and
  hardening behaviour but not persistence.

## 🤝 Contributing

Fork, branch, and open a pull request.

## 📄 License

MIT — see [LICENSE](./LICENSE).

## 📧 Contact

subhadip.dutta.18@gmail.com
