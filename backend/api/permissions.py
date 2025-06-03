"""permissions приложения."""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение для авторов и ro пользователей.

    Разрешает доступ на чтение всем пользователям,
    и лоступ на редактирование автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения для конкретного объекта."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
