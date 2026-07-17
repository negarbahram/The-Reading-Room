"""Aggregate queries backing the member and admin dashboards.

Definitions (also documented in docs/api.md):
  * Popularity        = completed + active loans within the selected date range.
  * Member activity    = total loans + returns within range.
  * On-time return rate = on-time returned loans / returned loans.
  * Outstanding balance = sum of UNPAID + PENDING_PAYMENT fines.
"""
from django.db.models import Case, Count, DecimalField, F, Q, Sum, When
from django.utils import timezone

from accounts.models import User
from catalog.models import Book, BookCopy
from circulation.models import Fine, Loan, LoanRequest, Reservation


def member_summary(user):
    loans = Loan.objects.filter(member=user)
    fines = Fine.objects.filter(member=user)
    return {
        'active_loans': loans.filter(status=Loan.Status.ACTIVE).count(),
        'overdue_loans': loans.filter(status=Loan.Status.OVERDUE).count(),
        'returned_loans': loans.filter(status=Loan.Status.RETURNED).count(),
        'pending_requests': user.loan_requests.filter(status='PENDING').count(),
        'active_reservations': Reservation.objects.filter(
            member=user, status__in=[Reservation.Status.WAITING, Reservation.Status.READY]
        ).count(),
        'outstanding_fines_total': fines.filter(
            status__in=[Fine.Status.UNPAID, Fine.Status.PENDING_PAYMENT]
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'unread_notifications': user.notifications.filter(is_read=False).count(),
    }


def _date_range_filter(queryset, field, date_from, date_to):
    if date_from:
        queryset = queryset.filter(**{f'{field}__gte': date_from})
    if date_to:
        queryset = queryset.filter(**{f'{field}__lte': date_to})
    return queryset


def admin_kpis():
    return {
        'total_books': Book.objects.filter(is_archived=False).count(),
        'total_copies': BookCopy.objects.exclude(status=BookCopy.Status.ARCHIVED).count(),
        'available_copies': BookCopy.objects.filter(status=BookCopy.Status.AVAILABLE).count(),
        'loaned_books': Loan.objects.filter(status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE]).count(),
        'overdue_loans': Loan.objects.filter(status=Loan.Status.OVERDUE).count(),
        'pending_requests': LoanRequest.objects.filter(status='PENDING').count(),
        'active_reservations': Reservation.objects.filter(
            status__in=[Reservation.Status.WAITING, Reservation.Status.READY]
        ).count(),
        'total_members': User.objects.filter(role=User.Role.MEMBER).count(),
        'outstanding_fines_total': Fine.objects.filter(
            status__in=[Fine.Status.UNPAID, Fine.Status.PENDING_PAYMENT]
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }


def inventory_report():
    """Available copies per book — calculated live, never a stored duplicate value."""
    books = Book.objects.filter(is_archived=False).select_related('author', 'genre').annotate(
        available=Count('copies', filter=Q(copies__status=BookCopy.Status.AVAILABLE)),
        total=Count('copies', filter=~Q(copies__status=BookCopy.Status.ARCHIVED)),
        on_loan=Count('copies', filter=Q(copies__status=BookCopy.Status.ON_LOAN)),
    )
    return [
        {
            'book_id': b.id, 'title': b.title, 'author': b.author.name, 'genre': b.genre.name,
            'available_copies': b.available, 'total_copies': b.total, 'on_loan_copies': b.on_loan,
        }
        for b in books
    ]


def overdue_activity():
    qs = Loan.objects.filter(status=Loan.Status.OVERDUE).select_related('member', 'book')
    now = timezone.now()
    return [
        {
            'loan_id': loan.id, 'member_email': loan.member.email, 'book_title': loan.book.title,
            'due_at': loan.due_at, 'days_overdue': (now.date() - loan.due_at.date()).days,
        }
        for loan in qs
    ]


def users_with_fines():
    qs = (
        User.objects.filter(fines__status__in=[Fine.Status.UNPAID, Fine.Status.PENDING_PAYMENT])
        .distinct()
        .annotate(
            outstanding_total=Sum(
                Case(
                    When(fines__status__in=[Fine.Status.UNPAID, Fine.Status.PENDING_PAYMENT], then=F('fines__amount')),
                    default=0, output_field=DecimalField(),
                )
            )
        )
    )
    return [{'user_id': u.id, 'email': u.email, 'outstanding_total': u.outstanding_total} for u in qs]


def popular_books(date_from=None, date_to=None, limit=20):
    qs = Loan.objects.filter(status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE, Loan.Status.RETURNED])
    qs = _date_range_filter(qs, 'borrowed_at', date_from, date_to)
    books = (
        Book.objects.filter(loans__in=qs)
        .annotate(loan_count=Count('loans', filter=Q(pk__in=qs.values('book_id'))))
        .order_by('-loan_count')[:limit]
        .select_related('author', 'genre')
    )
    return [
        {'book_id': b.id, 'title': b.title, 'author': b.author.name, 'loan_count': b.loan_count}
        for b in books
    ]


def member_performance(date_from=None, date_to=None, limit=50):
    loans = Loan.objects.all()
    loans = _date_range_filter(loans, 'borrowed_at', date_from, date_to)
    returned = loans.filter(status=Loan.Status.RETURNED)

    members = User.objects.filter(role=User.Role.MEMBER).annotate(
        total_loans=Count('loans', filter=Q(pk__in=loans.values('member_id')), distinct=False),
    )

    results = []
    for member in members:
        member_loans = loans.filter(member=member)
        member_returned = returned.filter(member=member)
        total = member_loans.count()
        returned_count = member_returned.count()
        on_time = member_returned.filter(returned_at__lte=F('due_at')).count()
        on_time_rate = round(on_time / returned_count, 2) if returned_count else None
        if total == 0:
            continue
        results.append({
            'user_id': member.id, 'email': member.email,
            'total_loans': total, 'returned_loans': returned_count,
            'on_time_return_rate': on_time_rate,
        })
    results.sort(key=lambda r: r['total_loans'], reverse=True)
    return results[:limit]
