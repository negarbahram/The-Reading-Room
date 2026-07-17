from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('loan-requests', views.LoanRequestViewSet, basename='loanrequest')
router.register('loans', views.LoanViewSet, basename='loan')
router.register('reservations', views.ReservationViewSet, basename='reservation')
router.register('fines', views.FineViewSet, basename='fine')

urlpatterns = router.urls
