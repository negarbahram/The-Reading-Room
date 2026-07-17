from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from .models import Review
from .serializers import ReviewSerializer


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.member == request.user or request.user.is_admin


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filterset_fields = ['book', 'is_approved']

    def get_queryset(self):
        qs = Review.objects.select_related('member', 'book')
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return qs
        return qs.filter(is_approved=True)

    def perform_create(self, serializer):
        from circulation.models import Loan
        book = serializer.validated_data['book']
        member = self.request.user
        has_borrowed = Loan.objects.filter(member=member, book=book).exists()
        if not has_borrowed:
            raise ValidationError('Only members who have borrowed this book may review it.')
        if Review.objects.filter(member=member, book=book).exists():
            raise ValidationError('You have already reviewed this book.')
        serializer.save(member=member)

    def perform_update(self, serializer):
        if serializer.instance.member != self.request.user and not self.request.user.is_admin:
            raise PermissionDenied('Cannot edit another member\'s review.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.member != self.request.user and not self.request.user.is_admin:
            raise PermissionDenied('Cannot delete another member\'s review.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def moderate(self, request, pk=None):
        from rest_framework.fields import BooleanField
        review = Review.objects.get(pk=pk)
        raw = request.data.get('is_approved')
        if raw is None:
            raise ValidationError('is_approved is required.')
        review.is_approved = BooleanField().to_internal_value(raw)
        review.save(update_fields=['is_approved'])
        return Response(ReviewSerializer(review).data)
