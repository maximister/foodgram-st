"""URLs для API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.users import UserViewSet
from api.views.recipes import (
    IngredientViewSet, RecipeViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
