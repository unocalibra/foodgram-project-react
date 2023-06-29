from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Basket, Favorite, Follow, Ingredient, IngredientIn,
                            Recipe, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиента."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов в рецепте для чтения."""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientIn
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов в рецепте для записи."""
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientIn
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тега."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class UserGetSerializer(UserSerializer):
    """
    Сериализатор данных о пользователе.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Определяем подписчиков."""
        request = self.context.get('request')
        return (request.user.is_authenticated and Follow.objects.
                filter(user=request.user, following__id=obj.id).exists())


class SignUpSerializer(UserCreateSerializer, UserGetSerializer):
    """
    Сериализатор регистрации.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'password')


class RecipeMinifieldSerializer(serializers.ModelSerializer):
    """
    Сериализатор краткой инф-ции модели рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранном!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMinifieldSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class UserFollowGetSerialazer(UserGetSerializer):
    """
    Сериализатор данных о подписках пользователя,
    его рецептах и их кол-ва.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Определяем рецепты автора."""
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author__id=obj.id).order_by('id')[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')
        return RecipeMinifieldSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Определяем сколько рецептов у автора."""
        return obj.recipes.count()


class UserFollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписки на пользователя.
    """
    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже итак подписаны.'
            )
        ]

    def validate(self, data):
        """Проверка на подписку на себя"""
        user = self.context["request"].user
        follow_obj = data["following"]
        if user == follow_obj:
            raise serializers.ValidationError(
                "Невозможно подписаться на самого себя!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserFollowGetSerialazer(
            instance.following, context={'request': request}
        ).data


class BasketSerializer(serializers.ModelSerializer):
    """Сериализатор корзины."""
    class Meta:
        model = Basket
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Basket.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в корзине.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMinifieldSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор информации о рецепте."""
    author = SignUpSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='ingredientsrecipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        """Определение избранных рецептов."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Определение продуктов в корзине."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Basket.objects.filter(user=request.user,
                                     recipe__id=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и изменения рецептов."""
    ingredients = IngredientPostSerializer(
        many=True, source='ingredientsrecipes'
    )
    author = SignUpSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate(self, value):
        """Проверка продуктов в рецепте."""
        ingredients_list = []
        for ingredient in value.get('ingredientsrecipes'):
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Кол-во не должно быть равным нулю.'
                )
            check_id = ingredient['ingredient']['id']
            check_ingredient = Ingredient.objects.filter(id=check_id)
            if not check_ingredient.exists():
                raise serializers.ValidationError(
                    'Данного продукта нет в базе!'
                )
            if check_ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Продукт уже есть в рецепте!'
                )
            ingredients_list.append(check_ingredient)
        return value

    def create_ingredients_tags(self, data_tags, ingredients, recipe):
        """Изменение тэгов и игнредиентов рецепта."""
        recipe.tags.add(*data_tags)
        ingredient_list = []
        for ingredient in ingredients:
            if not IngredientIn.objects.filter(
                ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredient_list.append(
                    IngredientIn(ingredient_id=ingredient['ingredient']['id'],
                                 recipe=recipe,
                                 amount=ingredient['amount']))
            else:
                raise serializers.ValidationError(
                    'Продукты уже есть в рецепте!')
        IngredientIn.objects.bulk_create(ingredient_list)
        return recipe

    def create(self, validated_data):
        """Создание рецепта."""
        data_tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientsrecipes')
        recipe = Recipe.objects.create(**validated_data)
        recipe = self.create_ingredients_tags(data_tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        data_tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientsrecipes')
        IngredientIn.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        instance = self.create_ingredients_tags(
            data_tags, ingredients, instance)
        super().update(instance, validated_data)
        return instance
