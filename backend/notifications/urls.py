from django.urls import path

from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification-read'),
    path('notifications/preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
]
