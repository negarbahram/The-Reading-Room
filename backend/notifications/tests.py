import pytest

from notifications.models import Notification
from notifications.services import notify


@pytest.mark.django_db
class TestNotificationDeduplication:
    def test_same_dedup_key_creates_one_notification(self, member):
        notify(member, 'loan_approved', 'msg one', dedup_key='fixed-key')
        notify(member, 'loan_approved', 'msg one retried', dedup_key='fixed-key')
        assert Notification.objects.filter(dedup_key='fixed-key').count() == 1

    def test_different_dedup_keys_create_separate_notifications(self, member):
        notify(member, 'loan_approved', 'msg one', dedup_key='key-1')
        notify(member, 'loan_approved', 'msg two', dedup_key='key-2')
        assert Notification.objects.filter(user=member).count() == 2

    def test_delivery_logs_created_for_enabled_channels(self, member):
        notification = notify(member, 'loan_approved', 'msg', dedup_key='key-logs')
        assert notification.delivery_logs.filter(channel='IN_APP').exists()
        assert notification.delivery_logs.filter(channel='EMAIL').exists()
        assert notification.delivery_logs.filter(channel='SMS').exists()
