from django.contrib import admin

from .models import Fine, LibraryPolicy, Loan, LoanRequest, Reservation


@admin.register(LibraryPolicy)
class LibraryPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(LoanRequest)
class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'status', 'requested_at']
    list_filter = ['status']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'status', 'borrowed_at', 'due_at', 'returned_at']
    list_filter = ['status']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'status', 'created_at', 'expires_at']
    list_filter = ['status']


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['member', 'loan', 'amount', 'status', 'created_at']
    list_filter = ['status']
