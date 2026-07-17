from decimal import Decimal

from django.conf import settings
from django.db import models


class LibraryPolicy(models.Model):
    """Singleton-style configurable policy. Admins may edit the single row."""
    loan_duration_days = models.PositiveIntegerField(default=14)
    max_concurrent_loans = models.PositiveIntegerField(default=5)
    grace_period_days = models.PositiveIntegerField(default=1)
    daily_late_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.50'))
    reservation_hold_days = models.PositiveIntegerField(default=3)
    allow_multiple_copies_same_title = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Library policy'

    def __str__(self):
        return 'Library Policy'

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class LoanRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_requests')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='loan_requests')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    decision_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-requested_at']
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'{self.member.email} → {self.book.title} ({self.status})'


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        OVERDUE = 'OVERDUE', 'Overdue'
        RETURNED = 'RETURNED', 'Returned'
        LOST = 'LOST', 'Lost'

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='loans')
    copy = models.ForeignKey('catalog.BookCopy', on_delete=models.PROTECT, related_name='loans')
    loan_request = models.OneToOneField(
        LoanRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='loan'
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-borrowed_at']
        indexes = [models.Index(fields=['status']), models.Index(fields=['due_at'])]

    def __str__(self):
        return f'{self.member.email} — {self.book.title} ({self.status})'


class Reservation(models.Model):
    class Status(models.TextChoices):
        WAITING = 'WAITING', 'Waiting'
        READY = 'READY', 'Ready for pickup'
        FULFILLED = 'FULFILLED', 'Fulfilled'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    held_copy = models.ForeignKey(
        'catalog.BookCopy', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations'
    )

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['status'])]
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'book'],
                condition=models.Q(status__in=['WAITING', 'READY']),
                name='unique_active_reservation_per_member_book',
            )
        ]

    def __str__(self):
        return f'{self.member.email} waiting on {self.book.title} ({self.status})'


class Fine(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pending payment'
        PAID = 'PAID', 'Paid'
        WAIVED = 'WAIVED', 'Waived'

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fines')
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UNPAID)
    reason = models.CharField(max_length=255, default='Late return')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    waived_reason = models.CharField(max_length=255, blank=True)
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'Fine {self.amount} for {self.member.email} ({self.status})'
