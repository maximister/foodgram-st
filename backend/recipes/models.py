"""Модели приложения recipes."""
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from recipes.constants import (
    MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT, MAX_NAME_LENGTH,
    COOKING_TIME_ERROR, INGREDIENT_AMOUNT_ERROR, USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH, USERNAME_REGEX
)


class User(AbstractUser):
    """Модель пользователя с расширенной функциональностью."""

    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[RegexValidator(
            regex=USERNAME_REGEX
        )]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        """Метаданные модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        swappable = 'AUTH_USER_MODEL'
        db_table = 'recipes_user'

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

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
        default_related_name = 'ingredients_in_recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            ),
        )

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
        default_related_name = '%(class)s'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            ),
        )

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


class ShoppingCart(UserRecipeRelation):
    """Модель списка покупок."""

    class Meta(UserRecipeRelation.Meta):
        """Метаданные модели списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(models.Model):
    """Модель подписки пользователей на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_from_authors',
        verbose_name='Автор',
    )

    class Meta:
        """Метаданные модели подписки."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            ),
        )

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f'{self.user} подписан на {self.author}'
