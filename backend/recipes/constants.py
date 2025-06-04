"""Константы для приложения."""
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 525600  # 1 год в минутах
MIN_INGREDIENT_AMOUNT = 1
MAX_NAME_LENGTH = 200
COOKING_TIME_ERROR = 'Время приготовления должно быть не менее 1 минуты'
MAX_COOKING_TIME_ERROR = 'Время приготовления не может быть больше 1 года'
INGREDIENT_AMOUNT_ERROR = 'Количество ингредиента должно быть не менее 1'

# Константы для админки
MIN_INGREDIENTS_IN_RECIPE = 1
EXTRA_INGREDIENT_FORMS = 1

# Константы для пользователей
USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150

USERNAME_REGEX = r'^[\w.@+-]+$'
