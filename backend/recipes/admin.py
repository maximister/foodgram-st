"""Админ-панель для приложения recipes."""
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from django.db.models import Min, Max
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import (
    Ingredient, Recipe, IngredientInRecipe, Favorite, ShoppingCart,
    User, Subscription
)
from recipes.constants import MIN_INGREDIENTS_IN_RECIPE, EXTRA_INGREDIENT_FORMS


class IngredientInRecipeInline(admin.TabularInline):
    """Инлайн для модели ингредиентов в рецепте."""

    model = IngredientInRecipe
    min_num = MIN_INGREDIENTS_IN_RECIPE
    extra = EXTRA_INGREDIENT_FORMS


class UsedInRecipesFilter(SimpleListFilter):
    """Фильтр для ингредиентов по наличию в рецептах."""

    title = 'Есть в рецептах'
    parameter_name = 'in_recipes'

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтрации."""
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, ingredients_queryset):
        """Фильтрует ингредиенты в зависимости от выбранного значения."""
        if self.value() == 'yes':
            return (ingredients_queryset
                    .filter(recipes__isnull=False)
                    .distinct())
        if self.value() == 'no':
            return ingredients_queryset.filter(recipes__isnull=True)
        return ingredients_queryset


class CookingTimeFilter(SimpleListFilter):
    """Фильтр рецептов по времени приготовления."""

    title = 'Время приготовления'
    parameter_name = 'cooking_time_category'

    def _get_thresholds(self):
        """Вычисляет пороговые значения для категорий времени приготовления."""
        stats = Recipe.objects.aggregate(
            min_time=Min('cooking_time'),
            max_time=Max('cooking_time')
        )

        if not stats['min_time'] or not stats['max_time']:
            return None, None, None

        min_time = stats['min_time']
        max_time = stats['max_time']

        if max_time - min_time < 60:
            fast_threshold = min(30, (min_time + max_time) // 2)
            medium_threshold = min(60, max_time)
        else:
            # При большом разбросе во времени границы вычисляются динамически
            step = (max_time - min_time) // 3
            fast_threshold = min_time + step
            medium_threshold = min_time + 2 * step

        return min_time, fast_threshold, medium_threshold

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтрации с динамическими порогами."""
        min_time, fast_threshold, medium_threshold = self._get_thresholds()

        if min_time is None:
            return (
                ('fast', 'Быстрые (до 30 мин)'),
                ('medium', 'Средние (до 60 мин)'),
                ('slow', 'Долгие (более 60 мин)'),
            )

        fast_count = Recipe.objects.filter(
            cooking_time__lte=fast_threshold
        ).count()
        medium_count = Recipe.objects.filter(
            cooking_time__gt=fast_threshold,
            cooking_time__lte=medium_threshold
        ).count()
        slow_count = Recipe.objects.filter(
            cooking_time__gt=medium_threshold
        ).count()

        fast_label = f'Быстрые (до {fast_threshold} мин) ({fast_count})'
        medium_label = f'Средние (до {medium_threshold} мин) ({medium_count})'
        slow_label = f'Долгие (более {medium_threshold} мин) ({slow_count})'

        return (
            ('fast', fast_label),
            ('medium', medium_label),
            ('slow', slow_label),
        )

    def queryset(self, request, recipes_queryset):
        """Фильтрует рецепты в зависимости от выбранного значения."""
        if not self.value():
            return recipes_queryset

        min_time, fast_threshold, medium_threshold = self._get_thresholds()

        if min_time is None:
            return recipes_queryset

        if self.value() == 'fast':
            return recipes_queryset.filter(cooking_time__lte=fast_threshold)
        elif self.value() == 'medium':
            return recipes_queryset.filter(
                cooking_time__gt=fast_threshold,
                cooking_time__lte=medium_threshold
            )
        elif self.value() == 'slow':
            return recipes_queryset.filter(cooking_time__gt=medium_threshold)

        return recipes_queryset


class HasRecipesFilter(SimpleListFilter):
    """Фильтр для пользователей по наличию рецептов."""

    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтрации."""
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users_queryset):
        """Фильтрует пользователей в зависимости от выбранного значения."""
        if self.value() == 'yes':
            return users_queryset.filter(recipes__isnull=False).distinct()
        if self.value() == 'no':
            return users_queryset.filter(recipes__isnull=True)
        return users_queryset


class HasSubscriptionsFilter(SimpleListFilter):
    """Фильтр для пользователей по наличию подписок."""

    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтрации."""
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users_queryset):
        """Фильтрует пользователей в зависимости от выбранного значения."""
        if self.value() == 'yes':
            return users_queryset.filter(
                subscriptions__isnull=False
            ).distinct()
        if self.value() == 'no':
            return users_queryset.filter(subscriptions__isnull=True)
        return users_queryset


class HasSubscribersFilter(SimpleListFilter):
    """Фильтр для пользователей по наличию подписчиков."""

    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтрации."""
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users_queryset):
        """Фильтрует пользователей в зависимости от выбранного значения."""
        if self.value() == 'yes':
            return users_queryset.filter(
                subscriptions_from_authors__isnull=False
            ).distinct()
        if self.value() == 'no':
            return users_queryset.filter(
                subscriptions_from_authors__isnull=True
            )
        return users_queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для модели пользователя."""

    list_display = (
        'id', 'username', 'get_full_name_display', 'email',
        'get_avatar', 'get_recipes_count', 'get_subscriptions_count',
        'get_subscribers_count',
    )
    list_filter = (
        'is_staff', 'is_superuser',
        HasRecipesFilter, HasSubscriptionsFilter, HasSubscribersFilter,
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password',)}),
        ('Персональная информация', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'avatar',
            )
        }),
        ('Права доступа', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined',)
        }),
    )

    @admin.display(description='ФИО')
    def get_full_name_display(self, user):
        """Возвращает полное имя пользователя."""
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar(self, user):
        """Возвращает HTML-разметку с аватаром пользователя."""
        if user.avatar:
            return f'<img src="{user.avatar.url}" width="50" height="50" />'
        return 'Нет аватара'

    @admin.display(description='Рецептов')
    def get_recipes_count(self, user):
        """Возвращает количество рецептов пользователя."""
        return user.recipes.count()

    @admin.display(description='Подписок')
    def get_subscriptions_count(self, user):
        """Возвращает количество подписок пользователя."""
        return user.subscriptions.count()

    @admin.display(description='Подписчиков')
    def get_subscribers_count(self, user):
        """Возвращает количество подписчиков пользователя."""
        return user.subscriptions_from_authors.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для модели ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', UsedInRecipesFilter)

    @admin.display(description='Рецептов')
    def recipes_count(self, ingredient):
        """Возвращает количество рецептов, использующих ингредиент."""
        return ingredient.recipes.count()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для модели рецептов."""

    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorites_count', 'get_ingredients', 'get_image'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('author', CookingTimeFilter)
    inlines = (IngredientInRecipeInline,)
    readonly_fields = ('favorites_count', 'get_ingredients', 'get_image')

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        """Возвращает количество добавлений рецепта в избранное."""
        return recipe.favorited.count()

    @admin.display(description='Ингредиенты')
    @mark_safe
    def get_ingredients(self, recipe):
        """Возвращает HTML-список ингредиентов рецепта."""
        ingredients = recipe.ingredients_in_recipes.all()
        if not ingredients:
            return 'Нет ингредиентов'

        ingredients_list = []
        for ingredient_in_recipe in ingredients:
            ingredients_list.append(
                f'{ingredient_in_recipe.ingredient.name} '
                f'({ingredient_in_recipe.amount} '
                f'{ingredient_in_recipe.ingredient.measurement_unit}) '
            )
        return '<br>'.join(ingredients_list)

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, recipe):
        """Возвращает HTML-разметку с изображением рецепта."""
        if recipe.image:
            return f'<img src="{recipe.image.url}" width="100" height="100" />'
        return 'Нет изображения'


@admin.register(Favorite, ShoppingCart)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    """Админ-панель для моделей связи пользователя и рецепта."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для модели подписки."""

    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)
