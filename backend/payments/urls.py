from django.urls import path

from . import views

urlpatterns = [
    path('payments/checkout/', views.CreateCheckoutSessionView.as_view(), name='payment-checkout'),
    path('payments/history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('payments/webhook/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    path('payments/<int:pk>/', views.PaymentStatusView.as_view(), name='payment-status'),
    path('payments/<int:pk>/confirm/', views.MockPayConfirmView.as_view(), name='payment-confirm'),
    path('payments/<int:pk>/receipt/', views.PaymentReceiptView.as_view(), name='payment-receipt'),
]
