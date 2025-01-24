from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение доступа: если не автор, то только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
