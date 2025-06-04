"""Сериализаторы для API рецептов чтобы flake8 не ругался."""
from django.db import transaction
from rest_framework import serializers

from recipes.models import (
    Ingredient, Recipe, IngredientInRecipe, Favorite, ShoppingCart
)
from recipes.constants import MIN_COOKING_TIME
from api.serializers.users import UserSerializer
from api.fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиента с рецептом."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов с количеством при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_in_recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        """Проверяет, добавлен ли рецепт в избранное."""
        request = self.context.get('request')
        return request and request.user.is_authenticated and \
            Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет, добавлен ли рецепт в список покупок."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(required=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Проверяет данные рецепта."""
        method = self.context['request'].method
        if method in ['PUT', 'PATCH'] and 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле обязательно.'}
            )
        return data

    def validate_image(self, image):
        """Проверяет изображение."""
        if not image:
            raise serializers.ValidationError(
                'Изображение обязательно.'
            )
        return image

    def validate_ingredients(self, ingredients):
        """Проверяет ингредиенты."""
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент'
            )

        ingredients_ids = [item['id'].id for item in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )

        return ingredients

    def create_ingredients(self, recipe, ingredients_data):
        """Создает записи ингредиентов для рецепта."""
        IngredientInRecipe.objects.bulk_create(
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients')

        recipe = super().create(validated_data)

        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients_in_recipes.all().delete()
        self.create_ingredients(instance, ingredients_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Преобразует данные модели в формат ответа."""
        return RecipeListSerializer(
            instance, context=self.context
        ).data


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    class Meta:
        """Метаданные сериализатора чтобы flake8 не ругался."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields
 