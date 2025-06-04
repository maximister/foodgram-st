"""Представления для приложения recipes."""
from django.shortcuts import redirect
from django.views import View
from django.http import Http404

from recipes.models import Recipe


class RecipeShortLinkView(View):
    """Представление для обработки коротких ссылок на рецепты."""

    def get(self, request, recipe_id):
        """Обрабатывает GET-запрос для перенаправления на страницу рецепта."""
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise Http404('Рецепт не найден')
        return redirect(f'/recipes/{recipe_id}')
