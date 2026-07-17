from django.contrib import admin

from .models import Payment, PaymentEvent


class PaymentEventInline(admin.TabularInline):
    model = PaymentEvent
    extra = 0
    readonly_fields = ['event_type', 'detail', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'fine', 'amount', 'status', 'created_at']
    list_filter = ['status']
    inlines = [PaymentEventInline]
