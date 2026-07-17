from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Full server-side enforcement — never trust the frontend for role checks."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """Catalog browsing is public; writes require an authenticated admin."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = getattr(obj, 'user', obj)
        return bool(user.is_admin or owner == user)


class IsNotSuspended(BasePermission):
    message = 'Your account is suspended and cannot perform this action.'

    def has_permission(self, request, view):
        return not getattr(request.user, 'is_suspended', False)