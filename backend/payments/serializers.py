from rest_framework import serializers

from .models import Payment, PaymentEvent


class PaymentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEvent
        fields = ['id', 'event_type', 'detail', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    events = PaymentEventSerializer(many=True, read_only=True)
    fine_reason = serializers.CharField(source='fine.reason', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'member', 'fine', 'fine_reason', 'amount', 'status',
            'session_id', 'created_at', 'updated_at', 'events',
        ]
        read_only_fields = fields


class CreateCheckoutSessionSerializer(serializers.Serializer):
    fine = serializers.IntegerField()
