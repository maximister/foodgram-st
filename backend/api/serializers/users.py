from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer

from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):    
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):    
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class SetPasswordSerializer(serializers.Serializer):    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Неверный текущий пароль.'
            )
        return value


class SetAvatarSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ('avatar',)


class RecipeMinifiedSerializer(serializers.Serializer):    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)


class UserWithRecipesSerializer(UserSerializer):    
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        
        from django.db.models import Model
        Recipe = type('Recipe', (Model,), {})
        
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
                
        return RecipeMinifiedSerializer(recipes, many=True).data
    
    def get_recipes_count(self, obj):
        from django.db.models import Model
        Recipe = type('Recipe', (Model,), {})
        
        return Recipe.objects.filter(author=obj).count() 
