from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.users import UserViewSet
from api.views.recipes import (
    IngredientViewSet, RecipeViewSet
)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
