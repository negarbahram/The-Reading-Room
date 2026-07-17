"""Domain services for circulation. Kept as plain functions (no unnecessary
service-layer abstraction) but centralised here so views stay thin and every
inventory/money-affecting operation goes through one transactional path.
"""
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from catalog.models import Book, BookCopy
from notifications.services import notify

from .models import Fine, Loan, LibraryPolicy, LoanRequest, Reservation


class CirculationError(ValidationError):
    pass


def _policy():
    return LibraryPolicy.current()


def create_loan_request(member, book: Book) -> LoanRequest:
    if member.is_suspended:
        raise CirculationError('Suspended members cannot submit loan requests.')

    policy = _policy()
    active_loans = Loan.objects.filter(member=member, status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE]).count()
    if active_loans >= policy.max_concurrent_loans:
        raise CirculationError('You have reached the maximum number of concurrent loans.')

    if not policy.allow_multiple_copies_same_title:
        already_borrowing = Loan.objects.filter(
            member=member, book=book, status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE]
        ).exists()
        if already_borrowing:
            raise CirculationError('You already have an active loan for this title.')

    if LoanRequest.objects.filter(member=member, book=book, status=LoanRequest.Status.PENDING).exists():
        raise CirculationError('You already have a pending request for this book.')

    return LoanRequest.objects.create(member=member, book=book)


def cancel_loan_request(loan_request: LoanRequest, actor):
    if loan_request.member != actor and not actor.is_admin:
        raise CirculationError('Not permitted to cancel this request.')
    if loan_request.status != LoanRequest.Status.PENDING:
        raise CirculationError('Only pending requests can be cancelled.')
    loan_request.status = LoanRequest.Status.CANCELLED
    loan_request.decided_at = timezone.now()
    loan_request.save(update_fields=['status', 'decided_at'])
    return loan_request


@transaction.atomic
def approve_loan_request(loan_request: LoanRequest, admin) -> Loan:
    loan_request = LoanRequest.objects.select_for_update().get(pk=loan_request.pk)
    if loan_request.status != LoanRequest.Status.PENDING:
        raise CirculationError('Only pending requests can be approved.')

    copy = (
        BookCopy.objects.select_for_update()
        .filter(book=loan_request.book, status=BookCopy.Status.AVAILABLE)
        .order_by('id')
        .first()
    )
    if copy is None:
        raise CirculationError('No available copy to allocate. Consider directing the member to reserve.')

    copy.status = BookCopy.Status.ON_LOAN
    copy.save(update_fields=['status'])

    loan_request.status = LoanRequest.Status.APPROVED
    loan_request.decided_at = timezone.now()
    loan_request.decided_by = admin
    loan_request.save(update_fields=['status', 'decided_at', 'decided_by'])

    policy = _policy()
    due_at = timezone.now() + timedelta(days=policy.loan_duration_days)
    loan = Loan.objects.create(
        member=loan_request.member, book=loan_request.book, copy=copy,
        loan_request=loan_request, due_at=due_at,
    )
    notify(
        loan.member, 'loan_approved',
        f'Your request for "{loan.book.title}" was approved. Due back {due_at.date()}.',
        dedup_key=f'loan_approved:{loan.id}',
    )
    return loan


@transaction.atomic
def reject_loan_request(loan_request: LoanRequest, admin, reason: str = '') -> LoanRequest:
    loan_request = LoanRequest.objects.select_for_update().get(pk=loan_request.pk)
    if loan_request.status != LoanRequest.Status.PENDING:
        raise CirculationError('Only pending requests can be rejected.')
    loan_request.status = LoanRequest.Status.REJECTED
    loan_request.decided_at = timezone.now()
    loan_request.decided_by = admin
    loan_request.decision_reason = reason
    loan_request.save(update_fields=['status', 'decided_at', 'decided_by', 'decision_reason'])
    notify(
        loan_request.member, 'loan_rejected',
        f'Your request for "{loan_request.book.title}" was rejected.' + (f' Reason: {reason}' if reason else ''),
        dedup_key=f'loan_rejected:{loan_request.id}',
    )
    return loan_request


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_fine_amount(loan: Loan, as_of=None) -> Decimal:
    """Deterministic fine calc: days late beyond grace period * daily rate."""
    policy = _policy()
    as_of = as_of or timezone.now()
    reference_return = loan.returned_at or as_of
    if reference_return <= loan.due_at:
        return Decimal('0.00')
    days_late = (reference_return.date() - loan.due_at.date()).days
    billable_days = max(days_late - policy.grace_period_days, 0)
    return _round_money(Decimal(billable_days) * policy.daily_late_fee)


@transaction.atomic
def checkout_loan_request(loan_request: LoanRequest, admin) -> Loan:
    """Alias path when 'approve' and 'checkout' are the same physical event."""
    return approve_loan_request(loan_request, admin)


@transaction.atomic
def return_loan(loan: Loan) -> Loan:
    loan = Loan.objects.select_for_update().get(pk=loan.pk)
    if loan.status in (Loan.Status.RETURNED, Loan.Status.LOST):
        return loan  # idempotent: repeated calls are safe no-ops

    loan.returned_at = timezone.now()
    loan.status = Loan.Status.RETURNED
    loan.save(update_fields=['returned_at', 'status'])

    fine_amount = calculate_fine_amount(loan)
    if fine_amount > 0:
        Fine.objects.create(member=loan.member, loan=loan, amount=fine_amount)
        notify(
            loan.member, 'fine_assessed',
            f'A late fee of ${fine_amount} was assessed for "{loan.book.title}".',
            dedup_key=f'fine_assessed:{loan.id}',
        )

    copy = BookCopy.objects.select_for_update().get(pk=loan.copy_id)
    promoted = _promote_next_reservation(loan.book, copy)
    if not promoted:
        copy.status = BookCopy.Status.AVAILABLE
        copy.save(update_fields=['status'])

    return loan


@transaction.atomic
def mark_loan_lost(loan: Loan) -> Loan:
    loan = Loan.objects.select_for_update().get(pk=loan.pk)
    loan.status = Loan.Status.LOST
    loan.returned_at = timezone.now()
    loan.save(update_fields=['status', 'returned_at'])
    copy = BookCopy.objects.select_for_update().get(pk=loan.copy_id)
    copy.status = BookCopy.Status.LOST
    copy.save(update_fields=['status'])
    return loan


def _promote_next_reservation(book: Book, copy: BookCopy) -> bool:
    """FIFO promotion. Copy is passed in already locked by the caller."""
    next_res = (
        Reservation.objects.select_for_update()
        .filter(book=book, status=Reservation.Status.WAITING)
        .order_by('created_at')
        .first()
    )
    if next_res is None:
        return False

    policy = _policy()
    copy.status = BookCopy.Status.HELD
    copy.save(update_fields=['status'])

    next_res.status = Reservation.Status.READY
    next_res.ready_at = timezone.now()
    next_res.expires_at = timezone.now() + timedelta(days=policy.reservation_hold_days)
    next_res.held_copy = copy
    next_res.save(update_fields=['status', 'ready_at', 'expires_at', 'held_copy'])

    notify(
        next_res.member, 'reservation_ready',
        f'"{book.title}" is ready for pickup. Hold expires {next_res.expires_at.date()}.',
        dedup_key=f'reservation_ready:{next_res.id}',
    )
    return True


@transaction.atomic
def create_reservation(member, book: Book) -> Reservation:
    if member.is_suspended:
        raise CirculationError('Suspended members cannot create reservations.')
    if Reservation.objects.filter(
        member=member, book=book, status__in=[Reservation.Status.WAITING, Reservation.Status.READY]
    ).exists():
        raise CirculationError('You already have an active reservation for this book.')
    if book.available_copies_count > 0:
        raise CirculationError('Copies are available — submit a loan request instead of a reservation.')

    reservation = Reservation.objects.create(member=member, book=book)
    notify(
        member, 'reservation_created',
        f'You are on the waitlist for "{book.title}".',
        dedup_key=f'reservation_created:{reservation.id}',
    )
    return reservation


def cancel_reservation(reservation: Reservation, actor) -> Reservation:
    if reservation.member != actor and not actor.is_admin:
        raise CirculationError('Not permitted to cancel this reservation.')
    if reservation.status not in (Reservation.Status.WAITING, Reservation.Status.READY):
        raise CirculationError('Only waiting or ready reservations can be cancelled.')

    with transaction.atomic():
        was_ready = reservation.status == Reservation.Status.READY
        held_copy = reservation.held_copy
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=['status'])

        if was_ready and held_copy:
            copy = BookCopy.objects.select_for_update().get(pk=held_copy.pk)
            promoted = _promote_next_reservation(reservation.book, copy)
            if not promoted:
                copy.status = BookCopy.Status.AVAILABLE
                copy.save(update_fields=['status'])
    return reservation


@transaction.atomic
def expire_reservations() -> int:
    """Release READY reservations whose hold window has passed. Idempotent."""
    now = timezone.now()
    expired = list(
        Reservation.objects.select_for_update().filter(
            status=Reservation.Status.READY, expires_at__lt=now
        )
    )
    for reservation in expired:
        copy = BookCopy.objects.select_for_update().get(pk=reservation.held_copy_id)
        reservation.status = Reservation.Status.EXPIRED
        reservation.save(update_fields=['status'])
        notify(
            reservation.member, 'reservation_expired',
            f'Your hold on "{reservation.book.title}" has expired.',
            dedup_key=f'reservation_expired:{reservation.id}',
        )
        promoted = _promote_next_reservation(reservation.book, copy)
        if not promoted:
            copy.status = BookCopy.Status.AVAILABLE
            copy.save(update_fields=['status'])
    return len(expired)


@transaction.atomic
def refresh_overdue_status() -> int:
    """Flip ACTIVE loans past due_at to OVERDUE. Idempotent, safe to re-run."""
    now = timezone.now()
    qs = Loan.objects.select_for_update().filter(status=Loan.Status.ACTIVE, due_at__lt=now)
    count = qs.count()
    for loan in qs:
        loan.status = Loan.Status.OVERDUE
        loan.save(update_fields=['status'])
        notify(
            loan.member, 'loan_overdue',
            f'"{loan.book.title}" is overdue. Please return it as soon as possible.',
            dedup_key=f'loan_overdue:{loan.id}:{now.date()}',
        )
    return count
