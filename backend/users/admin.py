"""Админ-панель для приложения users."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter

from .models import User, Subscription


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для модели подписки."""

    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)
