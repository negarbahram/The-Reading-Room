import uuid

from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCEEDED = 'SUCCEEDED', 'Succeeded'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    fine = models.ForeignKey('circulation.Fine', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    session_id = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    idempotency_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'Payment {self.session_id} — {self.amount} ({self.status})'


class PaymentEvent(models.Model):
    """Immutable audit trail — never mutated or deleted once written."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=32)
    detail = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.event_type} for payment {self.payment_id}'
