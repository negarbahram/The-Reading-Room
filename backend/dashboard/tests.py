from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from circulation.models import Fine, Loan
from dashboard import services


@pytest.mark.django_db
class TestDashboardMetrics:
    def test_admin_kpis_reflect_known_fixture(self, admin_user, member, book_with_copy):
        loan = Loan.objects.create(
            member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
            status=Loan.Status.ACTIVE, due_at=timezone.now() + timedelta(days=5),
        )
        Fine.objects.create(member=member, loan=loan, amount=Decimal('3.00'), status=Fine.Status.UNPAID)

        kpis = services.admin_kpis()
        assert kpis['loaned_books'] == 1
        assert kpis['outstanding_fines_total'] == Decimal('3.00')
        assert kpis['total_members'] == 1

    def test_popular_books_ranks_by_loan_count(self, member, member2, book, book_with_copy):
        from catalog.models import BookCopy
        c1 = book_with_copy.copies.first()
        Loan.objects.create(member=member, book=book_with_copy, copy=c1, status=Loan.Status.RETURNED,
                             due_at=timezone.now(), returned_at=timezone.now())
        c2 = BookCopy.objects.create(book=book_with_copy, barcode='BC-2')
        Loan.objects.create(member=member2, book=book_with_copy, copy=c2, status=Loan.Status.ACTIVE,
                             due_at=timezone.now() + timedelta(days=5))

        results = services.popular_books()
        assert results[0]['book_id'] == book_with_copy.id
        assert results[0]['loan_count'] == 2

    def test_member_performance_on_time_rate(self, member, book_with_copy):
        due = timezone.now() + timedelta(days=1)
        Loan.objects.create(
            member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
            status=Loan.Status.RETURNED, due_at=due, returned_at=due - timedelta(hours=1),
        )
        results = services.member_performance()
        entry = next(r for r in results if r['email'] == member.email)
        assert entry['on_time_return_rate'] == 1.0

    def test_users_with_fines_excludes_paid(self, member, book_with_copy):
        loan = Loan.objects.create(
            member=member, book=book_with_copy, copy=book_with_copy.copies.first(),
            due_at=timezone.now(),
        )
        Fine.objects.create(member=member, loan=loan, amount=Decimal('4.00'), status=Fine.Status.PAID)
        results = services.users_with_fines()
        assert results == []
