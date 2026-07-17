"""Manually-run reminder sweep (stands in for Celery Beat in this simplified
academic build). Run with: python manage.py send_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from circulation.models import Loan
from circulation.services import expire_reservations, refresh_overdue_status
from notifications.services import notify


class Command(BaseCommand):
    help = 'Send due-soon / due-today / overdue reminders and expire stale reservations.'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        due_soon_count = 0
        for loan in Loan.objects.filter(status=Loan.Status.ACTIVE):
            days_left = (loan.due_at.date() - today).days
            if days_left == 3:
                notify(
                    loan.member, 'loan_due_soon',
                    f'"{loan.book.title}" is due in 3 days ({loan.due_at.date()}).',
                    dedup_key=f'loan_due_soon:{loan.id}:{today}',
                )
                due_soon_count += 1
            elif days_left == 0:
                notify(
                    loan.member, 'loan_due_today',
                    f'"{loan.book.title}" is due today.',
                    dedup_key=f'loan_due_today:{loan.id}:{today}',
                )
                due_soon_count += 1

        overdue_count = refresh_overdue_status()
        expired_count = expire_reservations()

        self.stdout.write(self.style.SUCCESS(
            f'Reminders sent: {due_soon_count}. Newly overdue: {overdue_count}. '
            f'Reservations expired: {expired_count}.'
        ))
