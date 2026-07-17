from django.core.mail import send_mail

from .models import Notification, NotificationDeliveryLog, NotificationPreference
from .sms import get_sms_provider


def notify(user, event_type: str, message: str, dedup_key: str) -> Notification | None:
    """Create + deliver a notification. Idempotent via unique dedup_key —
    safe to call repeatedly (e.g. from retried tasks) without duplicating.
    """
    notification, created = Notification.objects.get_or_create(
        dedup_key=dedup_key,
        defaults={'user': user, 'event_type': event_type, 'message': message},
    )
    if not created:
        return notification

    prefs, _ = NotificationPreference.objects.get_or_create(user=user)

    if prefs.in_app_enabled:
        NotificationDeliveryLog.objects.create(notification=notification, channel='IN_APP', success=True)

    if prefs.email_enabled and user.email:
        try:
            send_mail(
                subject=f'Library notice: {notification.get_event_type_display()}',
                message=message,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )
            NotificationDeliveryLog.objects.create(notification=notification, channel='EMAIL', success=True)
        except Exception as exc:  # pragma: no cover - console backend never fails
            NotificationDeliveryLog.objects.create(
                notification=notification, channel='EMAIL', success=False, detail=str(exc)
            )

    if prefs.sms_enabled:
        provider = get_sms_provider()
        success = provider.send(user.phone_number, message)
        NotificationDeliveryLog.objects.create(notification=notification, channel='SMS', success=success)

    return notification
