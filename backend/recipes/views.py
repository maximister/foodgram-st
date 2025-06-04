"""Представления для приложения recipes."""
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from recipes.models import Recipe


class RecipeShortLinkView(View):
    """Представление для обработки коротких ссылок на рецепты."""

    def get(self, request, recipe_id):
        """Обрабатывает GET-запрос для перенаправления на страницу рецепта."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return redirect(f'/recipes/{recipe.id}')
