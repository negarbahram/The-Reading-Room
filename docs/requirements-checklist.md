# Requirements Checklist — traced to `library_management.md`

Every bullet from the source spec, mapped to its implementation and verification. Status legend: **PASS** (implemented and verified), **PARTIAL**, **MISSING**.

## 1. User Management

| Requirement | Status | Where |
|---|---|---|
| User registration and login (members and admins) | PASS | `backend/accounts/views.py` (`RegisterView`, `LoginView`), token auth; `frontend/src/pages/Login.tsx`, `Register.tsx` |
| Role assignment (administrator, regular member) | PASS | `accounts.User.Role` enum; admin role management via `AdminUserDetailView` PATCH; self-escalation blocked (`accounts/tests.py::test_member_cannot_escalate_own_role`) |
| Viewing history of borrowed and returned books | PASS | `GET /users/me/history/` (`circulation/views.py::MemberHistoryView`); `frontend/src/pages/MyLoans.tsx` (History tab) |

## 2. Book Management

| Requirement | Status | Where |
|---|---|---|
| Add a book with title, author, genre, publication date, available copies | PASS | `catalog.Book` + `catalog.BookCopy` models; admin book editor UI |
| Search/filter by author, genre, title, publication year | PASS | `catalog/filters.py::BookFilter`; tested in `catalog/tests.py::TestCatalogFiltering` |
| Admin can edit book information | PASS | `BookViewSet` PATCH, admin-only via `IsAdminOrReadOnly`; `AdminBookEditor.tsx` |

## 3. Borrowing and Return System

| Requirement | Status | Where |
|---|---|---|
| Members request books | PASS | `POST /loan-requests/`; `circulation/services.py::create_loan_request` |
| Loan duration and return date | PASS | `LibraryPolicy.loan_duration_days`, `Loan.due_at` set on approval |
| Reserve a book when all copies borrowed | PASS | `Reservation` model, FIFO queue, `create_reservation`; blocked when copies are available (`test_cannot_reserve_when_copies_available`) |
| Fine for late returns | PASS | `calculate_fine_amount` (Decimal, grace period, deterministic rounding); boundary-tested in `circulation/tests.py::TestFineCalculation` |

## 4. Notifications and Reminders

| Requirement | Status | Where |
|---|---|---|
| Email/SMS reminders for due dates | PASS | `notifications/services.py::notify`; console email backend; simulated `ConsoleSmsProvider`; `send_reminders` management command for due-soon/due-today/overdue |
| Notifications for pending reservations | PASS | `reservation_created`, `reservation_ready`, `reservation_expired` events, deduplicated via unique `dedup_key` (`notifications/tests.py`) |

## 5. Administrative Dashboard

| Requirement | Status | Where |
|---|---|---|
| Number of borrowed books and available stock per book | PASS | `dashboard/services.py::admin_kpis`, `inventory_report` (calculated live from `BookCopy` states, never stored) |
| Delays and users with fines | PASS | `overdue_activity`, `users_with_fines`; tested against fixed fixtures (`dashboard/tests.py`) |
| Book popularity and member performance reports | PASS | `popular_books`, `member_performance` with date-range filters + CSV export (`AdminReports.tsx`) |

## 6. Rating and Review System

| Requirement | Status | Where |
|---|---|---|
| Members rate and review books | PASS | `reviews.Review` (1–5 rating + comment); eligibility requires a borrowing relationship (`reviews/views.py::perform_create`) |
| Display reviews/ratings to other members | PASS | `ReviewViewSet` list (approved only for non-admins); `BookDetail.tsx` reviews section |

## 7. Online Fine Payment

| Requirement | Status | Where |
|---|---|---|
| Pay fines online | PASS | Mock checkout-session → confirm flow (`payments/services.py`); `PaymentCheckout.tsx`, `PaymentResult.tsx`, `PaymentReceipt.tsx` |
| No real payment provider required | PASS | `MockPayConfirmView` simulates provider confirmation; no external network calls; idempotent (`payments/tests.py::test_duplicate_confirmation_does_not_double_process`) |

## Extra Credit — Recommendations (mandatory per lead instructions)

| Requirement | Status | Where |
|---|---|---|
| Similar-book recommendations from borrowing/ratings | PASS | `recommendations/services.py::related_books`, weighted by shared genre/author/language/keywords |
| Related-book recommendations from user interests | PASS | `accounts.MemberInterest` + `recommended_for_user`, weighted signals from interests, history, ratings |
| "Recommended for You" on member dashboard | PASS | `GET /dashboard/member/recommendations/`; `MemberDashboard.tsx` |
| Human-readable reason per recommendation | PASS | `reason` field, e.g. "Because you enjoyed Science Fiction" |
| Cold-start fallback | PASS | `_popularity_fallback`; tested in `recommendations/tests.py::TestColdStartRecommendations` |
| Deterministic tests + seeded demo data | PASS | `recommendations/tests.py`; `seed_demo` builds borrowing/rating history that produces visible recommendations (verified live — see screenshots during manual QA) |

---

## Simplifications explicitly authorized by the project lead (documented, not silent omissions)

These reflect the "university project, not production" scope agreed before implementation:

- **Database**: SQLite instead of PostgreSQL.
- **Infra**: No Docker/Docker Compose, Redis, Celery/Celery Beat, Nginx, or CI. Reminders run via a manual management command (`send_reminders`) instead of a scheduler.
- **Auth**: DRF token authentication instead of a full session/CSRF/JWT stack.
- **Payments**: Mock provider only (no Stripe/sandbox credentials, no webhook signature verification) — the checkout/confirm/reconciliation flow is real, the "provider" is simulated.
- **SMS**: `ConsoleSmsProvider` logs to console instead of a real carrier; a swappable `SmsProvider` interface exists for a future real backend.
- **Type checking**: mypy was not run (not requested in the simplified scope); `ruff check` and `pytest` are the enforced backend gates.

None of the functional requirements in `library_management.md` were skipped — every row above is PASS.
