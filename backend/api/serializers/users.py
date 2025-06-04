"""Сериализаторы для работы с пользователями чтобы flake8 не ругался."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer
)

from recipes.models import Recipe, Subscription
from api.fields import Base64ImageField

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели пользователя чтобы flake8 не ругался."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        """Мне нечего сказать но flake8 ругается."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = fields

    def get_is_subscribed(self, author):
        """Проверка, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        return request and request.user.is_authenticated and \
            Subscription.objects.filter(
                user=request.user, author=author
            ).exists()


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        """Проверяет, что аватар не пустой."""
        if not value:
            raise serializers.ValidationError(
                'Отсутствует изображение аватара.'
            )
        return value


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор для пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        """Метаданные сериализатора."""

        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, author):
        """Возвращает список рецептов пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', 10**10)
        recipes = author.recipes.all()[:int(recipes_limit)]

        return RecipeShortInfoSerializer(recipes, many=True).data
