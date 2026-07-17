# Architecture (short version)

A modular-monolith Django project — one deployable backend, apps split by domain, no microservices or unnecessary service layers.

## Backend apps

| App | Owns |
|---|---|
| `accounts` | Custom `User` (email login, `ADMIN`/`MEMBER` roles), `MemberInterest`, auth endpoints, permissions |
| `catalog` | `Author`, `Genre`, `Book`, `BookCopy` — bibliographic vs. physical-copy split, search/filter |
| `circulation` | `LibraryPolicy`, `LoanRequest`, `Loan`, `Reservation`, `Fine` + all transactional business logic (`services.py`) |
| `notifications` | `Notification`, delivery logs, preferences, console email/SMS adapters, dedup-keyed `notify()` |
| `reviews` | `Review` — one per member/book, borrow-eligibility check, moderation |
| `payments` | `Payment`, `PaymentEvent` — mock checkout/confirm flow, idempotent, immutable audit trail |
| `recommendations` | Stateless rule-based scoring service (`related_books`, `recommended_for_user`); no dedicated models |
| `dashboard` | Read-only aggregate queries for member/admin dashboards and CSV reports |

Business logic lives in each app's `services.py` as plain functions wrapped in `@transaction.atomic` with `select_for_update()` for anything touching inventory or money — not in views, not behind heavyweight abstractions. Views stay thin: parse input, call a service, serialize the result.

## Concurrency-sensitive paths

- **Loan approval**: locks the `LoanRequest` row and locks+claims one `AVAILABLE` `BookCopy` row inside one transaction, so two concurrent approvals can never allocate the same copy (`circulation/tests.py::TestConcurrentAllocation`).
- **Return → reservation promotion**: locks the copy and the next `WAITING` reservation together; promotion, hold-expiry, and inventory release always happen atomically.
- **Payments**: `idempotency_key` and repeated-confirmation both short-circuit to a no-op, so retried requests/duplicate webhooks never double-charge or double-mark a fine paid.

## Frontend

React Router SPA. `AuthContext` holds the current user (token in `localStorage`); `RequireAuth` is a route guard for authenticated/admin-only routes — but the backend is the actual authority: every guarded backend endpoint checks `request.user.is_authenticated` / `is_admin` independently, so the frontend guard is a UX convenience, not the security boundary.

## Why not the full "enterprise" stack

The original brief specified Postgres/Redis/Celery/Docker/Nginx/CI. The project lead scoped this down to a university-project level (see `docs/requirements-checklist.md`, "Simplifications" section) — the domain logic, transactional safety, and every functional requirement are implemented for real; only the infrastructure around them was simplified.
