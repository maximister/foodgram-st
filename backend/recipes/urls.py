"""URLs для приложения recipes."""
from django.urls import path

from recipes.views import RecipeShortLinkView

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/',
        RecipeShortLinkView.as_view(),
        name='recipe-short-link'
    ),
]
