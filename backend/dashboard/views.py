import csv

from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from circulation.models import Loan, Reservation
from circulation.serializers import FineSerializer, LoanSerializer, ReservationSerializer
from circulation.models import Fine

from . import services


class MemberDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(services.member_summary(request.user))


class MemberActiveLoansView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Loan.objects.filter(member=request.user, status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE])
        return Response(LoanSerializer(qs, many=True).data)


class MemberReservationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Reservation.objects.filter(
            member=request.user, status__in=[Reservation.Status.WAITING, Reservation.Status.READY]
        )
        return Response(ReservationSerializer(qs, many=True).data)


class MemberOutstandingFinesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Fine.objects.filter(
            member=request.user, status__in=[Fine.Status.UNPAID, Fine.Status.PENDING_PAYMENT]
        )
        return Response(FineSerializer(qs, many=True).data)


class MemberRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from recommendations.services import recommended_for_user
        return Response(recommended_for_user(request.user))


class AdminKPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.admin_kpis())


class AdminInventoryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.inventory_report())


class AdminOverdueView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.overdue_activity())


class AdminUsersWithFinesView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.users_with_fines())


class AdminPopularBooksView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        data = services.popular_books(request.query_params.get('date_from'), request.query_params.get('date_to'))
        if request.query_params.get('format') == 'csv':
            return _csv_response(data, 'popular_books.csv')
        return Response(data)


class AdminMemberPerformanceView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        data = services.member_performance(request.query_params.get('date_from'), request.query_params.get('date_to'))
        if request.query_params.get('format') == 'csv':
            return _csv_response(data, 'member_performance.csv')
        return Response(data)


def _csv_response(rows, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())
    return response
