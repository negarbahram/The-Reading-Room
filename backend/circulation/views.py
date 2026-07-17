from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from catalog.models import Book

from . import services
from .models import Fine, LibraryPolicy, Loan, LoanRequest, Reservation
from .serializers import (
    FineAdjustSerializer, FineSerializer, LibraryPolicySerializer,
    LoanRequestSerializer, LoanSerializer, ReservationSerializer,
)


class LoanRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LoanRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        qs = LoanRequest.objects.select_related('book', 'member')
        if self.request.user.is_admin:
            return qs
        return qs.filter(member=self.request.user)

    def create(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=request.data.get('book'))
        loan_request = services.create_loan_request(request.user, book)
        return Response(LoanRequestSerializer(loan_request).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        loan_request = self.get_object()
        loan_request = services.cancel_loan_request(loan_request, request.user)
        return Response(LoanRequestSerializer(loan_request).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        loan_request = self.get_object()
        loan = services.approve_loan_request(loan_request, request.user)
        return Response(LoanSerializer(loan).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        loan_request = self.get_object()
        reason = request.data.get('reason', '')
        loan_request = services.reject_loan_request(loan_request, request.user, reason)
        return Response(LoanRequestSerializer(loan_request).data)


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    def get_queryset(self):
        qs = Loan.objects.select_related('book', 'member', 'copy')
        if self.request.user.is_admin:
            return qs
        return qs.filter(member=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='return')
    def do_return(self, request, pk=None):
        loan = self.get_object()
        loan = services.return_loan(loan)
        return Response(LoanSerializer(loan).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin], url_path='mark-lost')
    def mark_lost(self, request, pk=None):
        loan = self.get_object()
        loan = services.mark_loan_lost(loan)
        return Response(LoanSerializer(loan).data)


class MemberHistoryView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.select_related('book', 'copy').filter(member=self.request.user)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        qs = Reservation.objects.select_related('book', 'member')
        if self.request.user.is_admin:
            return qs
        return qs.filter(member=self.request.user)

    def create(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=request.data.get('book'))
        reservation = services.create_reservation(request.user, book)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation = services.cancel_reservation(reservation, request.user)
        return Response(ReservationSerializer(reservation).data)


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    def get_queryset(self):
        qs = Fine.objects.select_related('loan__book', 'member')
        if self.request.user.is_admin:
            return qs
        return qs.filter(member=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def adjust(self, request, pk=None):
        fine = self.get_object()
        serializer = FineAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['action'] == 'waive':
            fine.status = Fine.Status.WAIVED
            fine.waived_reason = serializer.validated_data['reason']
            fine.waived_by = request.user
            fine.resolved_at = timezone.now()
            fine.save(update_fields=['status', 'waived_reason', 'waived_by', 'resolved_at'])
        else:
            fine.status = Fine.Status.UNPAID
            fine.resolved_at = None
            fine.save(update_fields=['status', 'resolved_at'])
        return Response(FineSerializer(fine).data)


class LibraryPolicyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        policy = LibraryPolicy.current()
        return Response(LibraryPolicySerializer(policy).data)

    def patch(self, request):
        if not request.user.is_admin:
            return Response({'detail': 'Admin only.'}, status=403)
        policy = LibraryPolicy.current()
        serializer = LibraryPolicySerializer(policy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
