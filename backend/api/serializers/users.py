"""Сериализаторы для работы с пользователями."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)

from users.models import Subscription
from recipes.models import Recipe
from api.fields import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора."""

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

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def to_representation(self, instance):
        """Преобразует URL аватара в абсолютный."""
        ret = super().to_representation(instance)
        request = self.context.get('request')

        if instance.avatar and request:
            ret['avatar'] = request.build_absolute_uri(instance.avatar.url)

        return ret


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля."""

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        """Проверяет текущий пароль пользователя."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Неверный текущий пароль.'
            )
        return value


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        """Метаданные сериализатора."""

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


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор для пользователя с его рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        """Метаданные сериализатора."""

        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Возвращает список рецептов пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeShortInfoSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return Recipe.objects.filter(author=obj).count() 