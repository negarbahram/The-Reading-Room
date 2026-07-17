# The Reading Room — Online Library Management System

A university project implementing every requirement in [`library_management.md`](./library_management.md), including the extra-credit recommendation system, as a working full-stack app:

- **Backend**: Django 6 + Django REST Framework, SQLite, token authentication
- **Frontend**: React + TypeScript + Vite, Tailwind CSS
- **Simulated services**: console email backend, console-logging SMS provider, mock payment provider

This is deliberately built as a simple, understandable academic project — not a production system. See `docs/requirements-checklist.md` for the full requirement-by-requirement trace, and `docs/architecture.md` for a short design overview.

## Project structure

```
backend/     Django + DRF API (SQLite)
frontend/    React + TypeScript + Vite SPA
docs/        Requirements checklist, architecture notes
```

## Prerequisites

- Python 3.12+
- Node.js 20+ / npm

## 1. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo        # creates demo accounts, books, loans, fines, reviews
python manage.py runserver 8000
```

Backend runs at `http://localhost:8000`. API docs (Swagger UI) at `http://localhost:8000/api/docs/`. Health check: `http://localhost:8000/health/`.

## 2. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and talks to the backend at `http://localhost:8000/api/v1`.

## Demo accounts (created by `seed_demo`)

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@library.com` | `AdminPass123` |
| Member | `member1@library.com` … `member6@library.com` | `MemberPass123` |

`member1` has borrowing/rating history that produces visible personalized recommendations. `member6` has an unpaid fine ready to pay through the mock checkout flow. Two pending loan requests are seeded for the admin to approve/reject.

## Running reminders (stands in for a scheduler)

The spec's due-date/reservation reminders are implemented as a manual management command instead of Celery Beat (out of scope for this simplified build):

```bash
cd backend && source venv/bin/activate
python manage.py send_reminders
```

This sends due-soon/due-today/overdue notifications, flips overdue loans, and expires stale reservation holds. Notifications appear in-app (`/notifications`) and are logged to the console (email + SMS simulation).

## Tests

### Backend

```bash
cd backend
source venv/bin/activate
python -m pytest                          # run all tests
python -m pytest --cov=. --cov-report=term-missing   # with coverage
ruff check .                               # lint
```

74 tests covering: auth/permissions/role-escalation, catalog CRUD + filtering + available-copy calculation, concurrent-allocation race prevention, full loan/reservation/fine lifecycle with boundary dates, review eligibility/uniqueness/moderation, dashboard metrics against fixed fixtures, payment checkout/confirm/idempotency/reconciliation, and recommendation relevance + cold start.

### Frontend

```bash
cd frontend
npm run lint        # ESLint
npx tsc -b          # TypeScript strict type check
npm run test        # Vitest + React Testing Library unit tests
npm run build        # production build
```

### End-to-end (Playwright)

Requires both the backend (with seed data) and frontend dev servers running:

```bash
cd frontend
npx playwright install chromium   # first time only
npm run test:e2e
```

Covers: route guards (anonymous/member/admin), the full member browsing/dashboard workflow, and the full administrator console workflow.

## Troubleshooting

- **`database is locked` errors**: only run one `manage.py runserver` process at a time against `backend/db.sqlite3`. Check `ps aux | grep runserver` and kill duplicates.
- **Frontend can't reach the API**: confirm the backend is running on port 8000 and `frontend/src/api/client.ts`'s `API_BASE` matches.
- **CORS errors in the browser console**: the backend only allows `http://localhost:5173` / `127.0.0.1:5173` by default (`CORS_ALLOWED_ORIGINS` in `backend/config/settings.py`) — update it if you run the frontend on a different port.
- **Stale data after re-seeding**: `seed_demo` is idempotent (uses `get_or_create`) but won't undo manual changes made through the UI. Delete `backend/db.sqlite3` and re-run `migrate` + `seed_demo` for a clean slate.
- **Playwright browser not installed**: run `npx playwright install chromium` inside `frontend/`.

## Known limitations (by design, see `docs/requirements-checklist.md`)

- SQLite instead of PostgreSQL; no Docker/Redis/Celery — reminders run via a manual command instead of a live scheduler.
- Payments use a network-free mock provider — no real Stripe integration or webhook signature verification.
- SMS delivery is simulated via console logging behind a swappable `SmsProvider` interface.
- mypy was not run (not part of the agreed simplified scope); `ruff` + `pytest` are the enforced backend gates.
