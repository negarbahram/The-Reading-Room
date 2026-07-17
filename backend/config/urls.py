from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from circulation.views import LibraryPolicyView, MemberHistoryView


def health(request):
    return JsonResponse({'status': 'ok'})


def readiness(request):
    from django.db import connection
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    return JsonResponse({'status': 'ready' if db_ok else 'not ready', 'database': db_ok}, status=200 if db_ok else 503)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('readiness/', readiness, name='readiness'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('catalog.urls')),
    path('api/v1/', include('circulation.urls')),
    path('api/v1/users/me/history/', MemberHistoryView.as_view(), name='user-history'),
    path('api/v1/policy/', LibraryPolicyView.as_view(), name='library-policy'),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('reviews.urls')),
    path('api/v1/', include('payments.urls')),
    path('api/v1/', include('dashboard.urls')),
]
