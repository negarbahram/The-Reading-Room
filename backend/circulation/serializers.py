from rest_framework import serializers

from catalog.serializers import BookListSerializer

from .models import Fine, LibraryPolicy, Loan, LoanRequest, Reservation


class LoanRequestSerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source='book', read_only=True)
    member_email = serializers.CharField(source='member.email', read_only=True)

    class Meta:
        model = LoanRequest
        fields = [
            'id', 'member', 'member_email', 'book', 'book_detail', 'status',
            'requested_at', 'decided_at', 'decision_reason',
        ]
        read_only_fields = ['member', 'status', 'requested_at', 'decided_at', 'decision_reason']


class LoanSerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source='book', read_only=True)
    member_email = serializers.CharField(source='member.email', read_only=True)
    copy_barcode = serializers.CharField(source='copy.barcode', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 'member', 'member_email', 'book', 'book_detail', 'copy', 'copy_barcode',
            'status', 'borrowed_at', 'due_at', 'returned_at', 'is_overdue',
        ]

    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.status in (Loan.Status.ACTIVE, Loan.Status.OVERDUE) and obj.due_at < timezone.now()


class ReservationSerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source='book', read_only=True)
    member_email = serializers.CharField(source='member.email', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'member', 'member_email', 'book', 'book_detail', 'status',
            'created_at', 'ready_at', 'expires_at',
        ]
        read_only_fields = ['member', 'status', 'created_at', 'ready_at', 'expires_at']


class FineSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='loan.book.title', read_only=True)
    member_email = serializers.CharField(source='member.email', read_only=True)

    class Meta:
        model = Fine
        fields = [
            'id', 'member', 'member_email', 'loan', 'book_title', 'amount',
            'status', 'reason', 'created_at', 'resolved_at', 'waived_reason',
        ]
        read_only_fields = ['member', 'loan', 'amount', 'created_at', 'resolved_at']


class FineAdjustSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['waive', 'unwaive'])
    reason = serializers.CharField(required=True, allow_blank=False)


class LibraryPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryPolicy
        fields = [
            'id', 'loan_duration_days', 'max_concurrent_loans', 'grace_period_days',
            'daily_late_fee', 'reservation_hold_days', 'allow_multiple_copies_same_title',
        ]
