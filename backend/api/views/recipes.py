"""Представления для API рецептов."""
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.urls import reverse
import io

from recipes.models import (
    Ingredient, Recipe, IngredientInRecipe, Favorite, ShoppingCart
)
from api.serializers.recipes import (
    IngredientSerializer, RecipeListSerializer,
    RecipeCreateUpdateSerializer, RecipeShortInfoSerializer
)
from api.permissions import IsAuthorOrReadOnly
from api.pagination import FoodgramPagination
from api.filters import RecipeFilter, IngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ('create', 'partial_update', 'update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        """Создает рецепт с текущим пользователем в качестве автора."""
        serializer.save(author=self.request.user)

    def _handle_recipe_relation(self, request, pk, model):
        """Обрабатывает добавление/удаление рецепта из списка."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                verbose_name = model._meta.verbose_name.lower()
                return Response(
                    {'errors': f'Рецепт уже добавлен в {verbose_name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            relation = model.objects.create(user=user, recipe=recipe)

            serializer = RecipeShortInfoSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        relation = get_object_or_404(model, user=user, recipe=recipe)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Формирует короткую ссылку на рецепт."""
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        url = reverse('recipe-short-link', args=[pk])
        short_link = request.build_absolute_uri(url)
        return Response({'short-link': short_link})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в избранное."""
        return self._handle_recipe_relation(request, pk, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в список покупок."""
        return self._handle_recipe_relation(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок в формате TXT."""
        from datetime import datetime

        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        recipes = Recipe.objects.filter(
            in_shopping_carts__user=user
        ).select_related('author')

        current_date = datetime.now().strftime('%d.%m.%Y %H:%M')

        shopping_list = '\n'.join([
            f'Список покупок для {user.username}',
            f'Дата составления: {current_date}',
            '',
            'Продукты:',
            *[f"{i+1}. {item['ingredient__name'].capitalize()} "
              f"({item['ingredient__measurement_unit']}) - "
              f"{item['total_amount']}" for i, item in enumerate(ingredients)],
            '',
            'Рецепты:',
            *[f'{i+1}. {recipe.name} (Автор: {recipe.author.username})'
              for i, recipe in enumerate(recipes)],
        ])

        file_buffer = io.BytesIO(shopping_list.encode('utf-8'))

        return FileResponse(
            file_buffer,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )
 