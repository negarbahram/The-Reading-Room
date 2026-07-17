from decimal import Decimal

import pytest
from django.utils import timezone

from circulation.models import Fine, Loan
from payments import services
from payments.models import Payment


@pytest.fixture
def fine(db, member, book_with_copy):
    loan = Loan.objects.create(
        member=member, book=book_with_copy, copy=book_with_copy.copies.first(), due_at=timezone.now(),
    )
    return Fine.objects.create(member=member, loan=loan, amount=Decimal('5.00'))


@pytest.mark.django_db
class TestPaymentCheckout:
    def test_create_checkout_session(self, member, fine):
        payment = services.create_checkout_session(fine, member)
        assert payment.status == Payment.Status.PENDING
        fine.refresh_from_db()
        assert fine.status == Fine.Status.PENDING_PAYMENT

    def test_cannot_pay_already_paid_fine(self, member, fine):
        fine.status = Fine.Status.PAID
        fine.save()
        with pytest.raises(Exception):
            services.create_checkout_session(fine, member)

    def test_cannot_pay_someone_elses_fine(self, member2, fine):
        with pytest.raises(Exception):
            services.create_checkout_session(fine, member2)


@pytest.mark.django_db
class TestPaymentConfirmation:
    def test_successful_payment_marks_fine_paid(self, member, fine):
        payment = services.create_checkout_session(fine, member)
        payment = services.confirm_payment(payment, succeeded=True)
        assert payment.status == Payment.Status.SUCCEEDED
        fine.refresh_from_db()
        assert fine.status == Fine.Status.PAID

    def test_failed_payment_leaves_fine_recoverable(self, member, fine):
        payment = services.create_checkout_session(fine, member)
        payment = services.confirm_payment(payment, succeeded=False)
        assert payment.status == Payment.Status.FAILED
        fine.refresh_from_db()
        assert fine.status == Fine.Status.UNPAID  # recoverable — can retry

    def test_duplicate_confirmation_does_not_double_process(self, member, fine):
        payment = services.create_checkout_session(fine, member)
        services.confirm_payment(payment, succeeded=True)
        payment.refresh_from_db()
        events_before = payment.events.count()
        services.confirm_payment(payment, succeeded=True)  # simulated duplicate webhook
        payment.refresh_from_db()
        assert payment.events.count() == events_before
        assert payment.status == Payment.Status.SUCCEEDED

    def test_idempotency_key_reuses_same_payment(self, member, fine):
        p1 = services.create_checkout_session(fine, member, idempotency_key='fixed-key')
        p2 = services.create_checkout_session(fine, member, idempotency_key='fixed-key')
        assert p1.id == p2.id
        assert Payment.objects.filter(fine=fine).count() == 1


@pytest.mark.django_db
class TestPaymentReconciliation:
    def test_receipt_available_only_after_success(self, member, fine, api_client):
        payment = services.create_checkout_session(fine, member)
        api_client.force_authenticate(user=member)
        resp = api_client.get(f'/api/v1/payments/{payment.id}/receipt/')
        assert resp.status_code == 400

        services.confirm_payment(payment, succeeded=True)
        resp2 = api_client.get(f'/api/v1/payments/{payment.id}/receipt/')
        assert resp2.status_code == 200
