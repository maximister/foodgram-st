"""Представления для работы с пользователями."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.users import (
    UserSerializer, SetAvatarSerializer,
    UserWithRecipesSerializer
)
from api.pagination import FoodgramPagination
from recipes.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Представление для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgramPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает информацию о текущем пользователе."""
        return super().me(request)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновляет или удаляет аватар пользователя."""
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'Отсутствует поле avatar в запросе.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SetAvatarSerializer(
                instance=request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            avatar_url = request.build_absolute_uri(request.user.avatar.url)
            return Response(
                {'avatar': avatar_url},
                status=status.HTTP_200_OK
            )
        if request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.avatar = None
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Создает или удаляет подписку на автора."""
        if request.method == 'DELETE':
            Subscription.objects.filter(
                user=request.user, author_id=id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = get_object_or_404(User, id=id)

        if request.user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )

        if not created:
            return Response(
                {
                    'detail':
                    f'Вы уже подписаны на автора {author.username}.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserWithRecipesSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Возвращает подписки текущего пользователя."""
        subscriptions = User.objects.filter(
            subscriptions_from_authors__user=request.user
        )
        paginated_queryset = self.paginate_queryset(subscriptions)

        serializer = UserWithRecipesSerializer(
            paginated_queryset, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)
