from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор, или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorAdminModer(permissions.BasePermission):
    """Изменение администратором, автором, модератором."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


class IsAdmin(permissions.IsAdminUser):
    """Только для администратора."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
            )
        )
