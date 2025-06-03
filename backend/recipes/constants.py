"""Константы для рецептов."""
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 525600  # 365 дней в минутах (1 год)
MIN_INGREDIENT_AMOUNT = 1
MAX_NAME_LENGTH = 200
COOKING_TIME_ERROR = (
    f'Время приготовления должно быть не менее {MIN_COOKING_TIME} минуты'
)
MAX_COOKING_TIME_ERROR = (
    f'Время приготовления не может превышать {MAX_COOKING_TIME} минут (1 год)'
)
INGREDIENT_AMOUNT_ERROR = (
    f'Количество ингредиента должно быть не менее {MIN_INGREDIENT_AMOUNT}'
)

MIN_INGREDIENTS_IN_RECIPE = 1
EXTRA_INGREDIENT_FORMS = 1
