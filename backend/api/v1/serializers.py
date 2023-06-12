from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient,
                            Tag,
                            Recipe,
                            Favorite,
                            IngredientIn,
                            Basket,
                            Follow,
                            TagRecipe)
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиента."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов в рецепте для чтения."""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)

    class Meta:
        model = IngredientIn
        fields = ('id', 'name', 'unit', 'amount')


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
        fields = ('id', 'username', 'email', 'name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Определяем подписчиков."""
        request = self.context.get('request')
        return (request.user.is_authenticated and Follow.objects.
                filter(user=request.user, following__id=obj.id).exists())


class SignUpSerializer(UserCreateSerializer):
    """
    Сериализатор регистрации.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name',
                  'last_name', 'password')


class RecipeMinifieldSerializer(serializers.ModelSerializer):
    """
    Сериализатор краткой инф-ции модели рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'time', 'image')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipes')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранном.'
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
        fields = ('id', 'email', 'username', 'name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'name', 'last_name',
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
        request = self.context.get('request')
        if request.user == data['following']:
            raise serializers.ValidationError(
                'Подписаться на самого себя нельзя!'
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
    tag = TagSerializer(many=True)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='ingredientsrecipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_basket = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'description',
                  'ingredients', 'tag', 'time',
                  'is_in_basket', 'is_favorited')

    def get_is_favorited(self, obj):
        """Определение избранных рецептов."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Favorite.objects.filter(user=request.user,
                                   recipe__id=obj.id).exists():
            return True
        else:
            return False

    def get_is_in_basket(self, obj):
        """Определение продуктов в корзине."""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Basket.objects.filter(user=request.user,
                                 recipe__id=obj.id).exists():
            return True
        else:
            return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и изменения рецептов."""
    ingredients = IngredientPostSerializer(
        many=True, source='ingredientsrecipes'
    )
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                             many=True)
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'description',
                  'ingredients', 'tag', 'time',
                  'is_in_basket', 'is_favorited')

    def validate(self, value):
        """Проверка продуктов в рецепте."""
        ingredients_list = []
        ingredients = value
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
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
        for data_tag in data_tags:
            recipe.tag.add(data_tag)
            recipe.save()
        for ingredient in ingredients:
            if not IngredientIn.objects.filter(
                ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredientrecipe = IngredientIn.objects.create(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe)
                ingredientrecipe.amount = ingredient['amount']
                ingredient.save()
            else:
                IngredientIn.objects.filter(
                    recipe=recipe).delete()
                recipe.delete()
                raise serializers.ValidationError(
                    'Продукты уже есть в рецепте!')
        return recipe

    def create(self, validated_data):
        """Создание рецепта."""
        name = validated_data.get('name')
        data_tags = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredientrecipes')
        time = validated_data.get('time')
        description = validated_data.get('description')
        image = validated_data.get('image')
        author = validated_data.get('author')

        recipe = Recipe.objects.create(
            name=name,
            time=time,
            image=image,
            description=description,
            author=author
        )
        recipe = self.create_ingredients_tags(data_tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        data_tags = validated_data.pop('tag')
        ingredients = validated_data.pop('ingredientrecipes')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientIn.objects.filter(recipe=instance).delete()
        instance = self.create_ingredients_tags(
            data_tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance
