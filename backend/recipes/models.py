"""Модели приложения recipes."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from recipes.constants import (
    MIN_COOKING_TIME, MAX_COOKING_TIME, MIN_INGREDIENT_AMOUNT, MAX_NAME_LENGTH,
    COOKING_TIME_ERROR, MAX_COOKING_TIME_ERROR, INGREDIENT_AMOUNT_ERROR
)


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_NAME_LENGTH,
    )

    class Meta:
        """Метаданные модели ингредиента."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        """Строковое представление модели ингредиента."""
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGTH,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(
        'Описание',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME, message=COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                MAX_COOKING_TIME, message=MAX_COOKING_TIME_ERROR
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        """Метаданные модели рецепта."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', 'name')
        default_related_name = 'recipes'

    def __str__(self):
        """Строковое представление модели рецепта."""
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для связи ингредиента с рецептом и указания количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients_in_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            MIN_INGREDIENT_AMOUNT, message=INGREDIENT_AMOUNT_ERROR
        )]
    )

    class Meta:
        """Метаданные модели ингредиента в рецепте."""

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        """Строковое представление модели ингредиента в рецепте."""
        return (f'{self.ingredient.name} '
                f'({self.amount} {self.ingredient.measurement_unit})')


class UserRecipeRelation(models.Model):
    """Базовый абстрактный класс для связи пользователя и рецепта."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        """Метаданные абстрактного класса."""
        
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique'
            )
        ]
    
    def __str__(self):
        """Строковое представление связи пользователя и рецепта."""
        relation_type = self._meta.verbose_name.lower()
        return (f'{self.user.username} добавил '
                f'{self.recipe.name} в {relation_type}')


class Favorite(UserRecipeRelation):
    """Модель избранного."""

    class Meta(UserRecipeRelation.Meta):
        """Метаданные модели избранного."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorited'


class ShoppingCart(UserRecipeRelation):
    """Модель списка покупок."""

    class Meta(UserRecipeRelation.Meta):
        """Метаданные модели списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'in_shopping_carts'
