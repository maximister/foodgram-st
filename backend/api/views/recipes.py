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
        user = request.user

        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            relation, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                verbose_name = model._meta.verbose_name.lower()
                error = f'Рецепт "{recipe.name}" уже добавлен в {verbose_name}'
                return Response(
                    {'errors': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RecipeShortInfoSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        model.objects.filter(user=user, recipe_id=pk).delete()
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
                {'errors': f'Рецепт с ID {pk} не найден'},
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
            recipe__shoppingcart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        recipes = Recipe.objects.filter(
            shoppingcart__user=user
        ).select_related('author').order_by('name')

        current_date = datetime.now().strftime('%d.%m.%Y %H:%M')

        shopping_list = '\n'.join([
            f'Список покупок для {user.username}',
            f'Дата составления: {current_date}',
            '',
            'Продукты:',
            *[
                f"{i}. {item['ingredient__name'].capitalize()} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}"
                for i, item in enumerate(ingredients, start=1)
            ],
            '',
            'Рецепты:',
            *[
                f'{i}. {recipe.name} (Автор: {recipe.author.username})'
                for i, recipe in enumerate(recipes, start=1)
            ],
        ])

        return FileResponse(
            shopping_list,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )
