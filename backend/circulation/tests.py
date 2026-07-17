from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from catalog.models import BookCopy
from circulation import services
from circulation.models import Fine, Loan, LoanRequest, Reservation


@pytest.mark.django_db
class TestLoanRequestLifecycle:
    def test_create_request(self, member, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        assert lr.status == LoanRequest.Status.PENDING

    def test_duplicate_pending_request_rejected(self, member, book_with_copy):
        services.create_loan_request(member, book_with_copy)
        with pytest.raises(Exception):
            services.create_loan_request(member, book_with_copy)

    def test_suspended_member_cannot_request(self, member, book_with_copy):
        member.is_suspended = True
        member.save()
        with pytest.raises(Exception):
            services.create_loan_request(member, book_with_copy)

    def test_member_over_loan_limit_cannot_request(self, member, book_with_copy, policy, author, genre):
        policy.max_concurrent_loans = 0
        policy.save()
        with pytest.raises(Exception):
            services.create_loan_request(member, book_with_copy)

    def test_cancel_pending_request(self, member, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        lr = services.cancel_loan_request(lr, member)
        assert lr.status == LoanRequest.Status.CANCELLED

    def test_approve_allocates_copy_and_creates_loan(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        assert loan.status == Loan.Status.ACTIVE
        assert loan.copy.status == BookCopy.Status.ON_LOAN
        lr.refresh_from_db()
        assert lr.status == LoanRequest.Status.APPROVED

    def test_approve_without_available_copy_fails(self, member, admin_user, book):
        lr = services.create_loan_request(member, book)  # no copies at all
        with pytest.raises(Exception):
            services.approve_loan_request(lr, admin_user)

    def test_reject_request(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        lr = services.reject_loan_request(lr, admin_user, reason='Too many holds')
        assert lr.status == LoanRequest.Status.REJECTED
        assert lr.decision_reason == 'Too many holds'

    def test_second_approval_of_same_request_fails(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        services.approve_loan_request(lr, admin_user)
        with pytest.raises(Exception):
            services.approve_loan_request(lr, admin_user)


@pytest.mark.django_db
class TestConcurrentAllocation:
    def test_two_requests_one_copy_only_one_approved(self, member, member2, admin_user, book_with_copy):
        """Only one copy exists — approving both requests must not double-allocate it."""
        lr1 = services.create_loan_request(member, book_with_copy)
        lr2 = services.create_loan_request(member2, book_with_copy)

        services.approve_loan_request(lr1, admin_user)
        with pytest.raises(Exception):
            services.approve_loan_request(lr2, admin_user)

        assert Loan.objects.filter(book=book_with_copy).count() == 1


@pytest.mark.django_db
class TestReturnAndDueDate:
    def test_due_date_set_from_policy(self, member, admin_user, book_with_copy, policy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        expected = loan.borrowed_at + timedelta(days=policy.loan_duration_days)
        assert abs((loan.due_at - expected).total_seconds()) < 5

    def test_return_releases_copy(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        loan = services.return_loan(loan)
        assert loan.status == Loan.Status.RETURNED
        loan.copy.refresh_from_db()
        assert loan.copy.status == BookCopy.Status.AVAILABLE

    def test_return_is_idempotent(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        services.return_loan(loan)
        loan.refresh_from_db()
        returned_at_first = loan.returned_at
        loan2 = services.return_loan(loan)
        assert loan2.returned_at == returned_at_first

    def test_overdue_transition(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        Loan.objects.filter(pk=loan.pk).update(due_at=timezone.now() - timedelta(days=1))
        count = services.refresh_overdue_status()
        assert count == 1
        loan.refresh_from_db()
        assert loan.status == Loan.Status.OVERDUE


@pytest.mark.django_db
class TestFineCalculation:
    def test_no_fine_within_due_date(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        assert services.calculate_fine_amount(loan) == Decimal('0.00')

    def test_fine_zero_within_grace_period(self, member, admin_user, book_with_copy, policy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        # Grace period is 1 day: returning exactly 1 day late should not incur a fine.
        Loan.objects.filter(pk=loan.pk).update(due_at=timezone.now() - timedelta(days=1))
        loan.refresh_from_db()
        assert services.calculate_fine_amount(loan, as_of=timezone.now()) == Decimal('0.00')

    def test_fine_charged_beyond_grace_period(self, member, admin_user, book_with_copy, policy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        Loan.objects.filter(pk=loan.pk).update(due_at=timezone.now() - timedelta(days=4))
        loan.refresh_from_db()
        # 4 days late - 1 day grace = 3 billable days * 0.50
        assert services.calculate_fine_amount(loan, as_of=timezone.now()) == Decimal('1.50')

    def test_return_creates_fine_record(self, member, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        Loan.objects.filter(pk=loan.pk).update(due_at=timezone.now() - timedelta(days=5))
        loan.refresh_from_db()
        loan = services.return_loan(loan)
        fine = Fine.objects.get(loan=loan)
        assert fine.amount == Decimal('2.00')
        assert fine.status == Fine.Status.UNPAID


@pytest.mark.django_db
class TestReservations:
    def test_cannot_reserve_when_copies_available(self, member, book_with_copy):
        with pytest.raises(Exception):
            services.create_reservation(member, book_with_copy)

    def test_cannot_create_duplicate_active_reservation(self, member, member2, book):
        services.create_reservation(member, book)
        with pytest.raises(Exception):
            services.create_reservation(member, book)

    def test_fifo_promotion_on_return(self, member, member2, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)  # copy now taken
        res1 = services.create_reservation(member2, book_with_copy)

        loan = services.return_loan(loan)
        res1.refresh_from_db()
        assert res1.status == Reservation.Status.READY
        assert res1.held_copy_id == loan.copy_id

    def test_reservation_expiration_releases_copy_to_next(self, member, member2, admin_user, book_with_copy):
        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        res1 = services.create_reservation(member2, book_with_copy)
        services.return_loan(loan)
        res1.refresh_from_db()

        Reservation.objects.filter(pk=res1.pk).update(expires_at=timezone.now() - timedelta(hours=1))
        expired_count = services.expire_reservations()
        assert expired_count == 1
        res1.refresh_from_db()
        assert res1.status == Reservation.Status.EXPIRED

        copy = BookCopy.objects.get(pk=res1.held_copy_id)
        assert copy.status == BookCopy.Status.AVAILABLE

    def test_cancel_reservation_promotes_next_in_queue(self, member, member2, admin_user, book_with_copy):
        from accounts.models import User
        member3 = User.objects.create_user(email='member3@test.com', password='pass12345')

        lr = services.create_loan_request(member, book_with_copy)
        loan = services.approve_loan_request(lr, admin_user)
        res1 = services.create_reservation(member2, book_with_copy)
        services.create_reservation(member3, book_with_copy)
        services.return_loan(loan)
        res1.refresh_from_db()
        assert res1.status == Reservation.Status.READY

        services.cancel_reservation(res1, member2)

        res2 = Reservation.objects.get(member=member3, book=book_with_copy)
        assert res2.status == Reservation.Status.READY
