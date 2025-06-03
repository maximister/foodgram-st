"""Фильтры для рецептов и ингредиентов."""
from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов по имени."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        """Метаданные фильтра."""

        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        """Метаданные фильтра."""

        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'name')

    def filter_is_favorited(self, recipes, name, value):
        """Фильтрует рецепты по наличию в избранном."""
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(favorited_by__user=user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        """Фильтрует рецепты по наличию в списке покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return recipes.filter(in_shopping_carts__user=user)
        return recipes
