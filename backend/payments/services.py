import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from circulation.models import Fine
from notifications.services import notify

from .models import Payment, PaymentEvent


class PaymentError(ValidationError):
    pass


@transaction.atomic
def create_checkout_session(fine: Fine, member, idempotency_key: str | None = None) -> Payment:
    fine = Fine.objects.select_for_update().get(pk=fine.pk)
    if fine.member != member:
        raise PaymentError('This fine does not belong to you.')
    if fine.status == Fine.Status.PAID:
        raise PaymentError('This fine has already been paid.')
    if fine.status == Fine.Status.WAIVED:
        raise PaymentError('This fine has been waived and cannot be paid.')

    idempotency_key = idempotency_key or f'fine:{fine.id}:{uuid.uuid4()}'
    existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    pending = Payment.objects.filter(fine=fine, status=Payment.Status.PENDING).first()
    if pending:
        return pending

    payment = Payment.objects.create(
        member=member, fine=fine, amount=fine.amount, idempotency_key=idempotency_key,
    )
    PaymentEvent.objects.create(payment=payment, event_type='session_created')
    fine.status = Fine.Status.PENDING_PAYMENT
    fine.save(update_fields=['status'])
    return payment


@transaction.atomic
def confirm_payment(payment: Payment, succeeded: bool) -> Payment:
    """Simulated provider webhook / mock 'Pay' confirmation. Idempotent —
    calling this twice for the same payment has no additional effect.
    """
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status in (Payment.Status.SUCCEEDED, Payment.Status.FAILED, Payment.Status.CANCELLED):
        return payment  # already resolved; duplicate webhook is a no-op

    fine = Fine.objects.select_for_update().get(pk=payment.fine_id)

    if succeeded:
        payment.status = Payment.Status.SUCCEEDED
        payment.save(update_fields=['status'])
        fine.status = Fine.Status.PAID
        fine.resolved_at = timezone.now()
        fine.save(update_fields=['status', 'resolved_at'])
        PaymentEvent.objects.create(payment=payment, event_type='payment_succeeded')
        notify(
            payment.member, 'payment_success',
            f'Your payment of ${payment.amount} was received. Thank you.',
            dedup_key=f'payment_success:{payment.id}',
        )
    else:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status'])
        fine.status = Fine.Status.UNPAID  # recoverable — member can retry checkout
        fine.save(update_fields=['status'])
        PaymentEvent.objects.create(payment=payment, event_type='payment_failed')
        notify(
            payment.member, 'payment_failed',
            f'Your payment of ${payment.amount} failed. Please try again.',
            dedup_key=f'payment_failed:{payment.id}',
        )
    return payment


@transaction.atomic
def cancel_payment(payment: Payment) -> Payment:
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status != Payment.Status.PENDING:
        return payment
    payment.status = Payment.Status.CANCELLED
    payment.save(update_fields=['status'])
    fine = Fine.objects.select_for_update().get(pk=payment.fine_id)
    if fine.status == Fine.Status.PENDING_PAYMENT:
        fine.status = Fine.Status.UNPAID
        fine.save(update_fields=['status'])
    PaymentEvent.objects.create(payment=payment, event_type='payment_cancelled')
    return payment
