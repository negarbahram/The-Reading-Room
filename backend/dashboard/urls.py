from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/member/summary/', views.MemberDashboardView.as_view(), name='member-dashboard-summary'),
    path('dashboard/member/active-loans/', views.MemberActiveLoansView.as_view(), name='member-dashboard-loans'),
    path('dashboard/member/reservations/', views.MemberReservationsView.as_view(), name='member-dashboard-reservations'),
    path('dashboard/member/fines/', views.MemberOutstandingFinesView.as_view(), name='member-dashboard-fines'),
    path('dashboard/member/recommendations/', views.MemberRecommendationsView.as_view(), name='member-dashboard-recommendations'),

    path('dashboard/admin/kpis/', views.AdminKPIView.as_view(), name='admin-dashboard-kpis'),
    path('dashboard/admin/inventory/', views.AdminInventoryView.as_view(), name='admin-dashboard-inventory'),
    path('dashboard/admin/overdue/', views.AdminOverdueView.as_view(), name='admin-dashboard-overdue'),
    path('dashboard/admin/users-with-fines/', views.AdminUsersWithFinesView.as_view(), name='admin-dashboard-fines-users'),
    path('dashboard/admin/popular-books/', views.AdminPopularBooksView.as_view(), name='admin-dashboard-popular'),
    path('dashboard/admin/member-performance/', views.AdminMemberPerformanceView.as_view(), name='admin-dashboard-performance'),
]
