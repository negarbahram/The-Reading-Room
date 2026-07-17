from django.conf import settings
from django.db import models


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'Preferences for {self.user.email}'


class Notification(models.Model):
    class EventType(models.TextChoices):
        LOAN_APPROVED = 'loan_approved', 'Loan approved'
        LOAN_REJECTED = 'loan_rejected', 'Loan rejected'
        LOAN_DUE_SOON = 'loan_due_soon', 'Loan due soon'
        LOAN_DUE_TODAY = 'loan_due_today', 'Loan due today'
        LOAN_OVERDUE = 'loan_overdue', 'Loan overdue'
        FINE_ASSESSED = 'fine_assessed', 'Fine assessed'
        RESERVATION_CREATED = 'reservation_created', 'Reservation created'
        RESERVATION_READY = 'reservation_ready', 'Reservation ready'
        RESERVATION_EXPIRED = 'reservation_expired', 'Reservation expired'
        PAYMENT_SUCCESS = 'payment_success', 'Payment success'
        PAYMENT_FAILED = 'payment_failed', 'Payment failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    message = models.TextField()
    dedup_key = models.CharField(max_length=255, unique=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]

    def __str__(self):
        return f'{self.event_type} → {self.user.email}'


class NotificationDeliveryLog(models.Model):
    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        IN_APP = 'IN_APP', 'In-app'

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    channel = models.CharField(max_length=10, choices=Channel.choices)
    delivered_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    detail = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.channel} log for notification {self.notification_id}'
