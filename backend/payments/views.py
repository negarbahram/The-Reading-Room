from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from circulation.models import Fine

from . import services
from .models import Payment
from .serializers import CreateCheckoutSessionSerializer, PaymentSerializer


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fine = get_object_or_404(Fine, pk=serializer.validated_data['fine'])
        idempotency_key = request.headers.get('Idempotency-Key')
        payment = services.create_checkout_session(fine, request.user, idempotency_key)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if payment.member != request.user and not request.user.is_admin:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(PaymentSerializer(payment).data)


class MockPayConfirmView(APIView):
    """Stand-in for a real provider's webhook: the mock payment page calls this
    directly when the member clicks 'Pay' / 'Simulate failure'.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if payment.member != request.user:
            return Response({'detail': 'Not found.'}, status=404)
        succeeded = request.data.get('outcome', 'success') != 'fail'
        payment = services.confirm_payment(payment, succeeded)
        return Response(PaymentSerializer(payment).data)


class PaymentWebhookView(APIView):
    """Provider-facing webhook endpoint. In the mock provider this is invoked
    by MockPayConfirmView server-side, but it is also directly callable to
    demonstrate idempotent webhook handling.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        session_id = request.data.get('session_id')
        outcome = request.data.get('outcome', 'success')
        payment = get_object_or_404(Payment, session_id=session_id)
        payment = services.confirm_payment(payment, outcome != 'fail')
        return Response(PaymentSerializer(payment).data)


class PaymentReceiptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if payment.member != request.user and not request.user.is_admin:
            return Response({'detail': 'Not found.'}, status=404)
        if payment.status != Payment.Status.SUCCEEDED:
            return Response({'detail': 'Receipt is only available for successful payments.'}, status=400)
        return Response(PaymentSerializer(payment).data)


class PaymentHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Payment.objects.filter(member=request.user).select_related('fine')
        return Response(PaymentSerializer(qs, many=True).data)
