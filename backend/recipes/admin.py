from django.contrib import admin

from recipes.models import (
    Ingredient, Recipe, IngredientInRecipe, Favorite, ShoppingCart
)


class IngredientInRecipeInline(admin.TabularInline):
    """Инлайн-админка для модели ингредиентов в рецепте."""
    
    model = IngredientInRecipe
    min_num = 1
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для модели ингредиентов."""
    
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для модели рецептов."""
    
    list_display = ('id', 'name', 'author', 'cooking_time', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)
    inlines = (IngredientInRecipeInline,)
    readonly_fields = ('favorites_count',)
    
    def favorites_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return obj.favorited_by.count()
    
    favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для модели избранного."""
    
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель для модели списка покупок."""
    
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
