from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение доступа: если не автор, то только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор, или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            # and (request.user.is_superuser or request.user.is_staff)
        )

class IsAdmin(permissions.IsAdminUser):
    """Права для работы с пользователями."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            #and request.user.is_admin
        )
    