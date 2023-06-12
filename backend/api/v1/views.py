from django.db.models import Sum
from api.v1.serializers import (IngredientSerializer,
                                TagSerializer, BasketSerializer,
                                SignUpSerializer, UserFollowSerializer,
                                UserFollowGetSerialazer,
                                RecipeCreateSerializer,
                                RecipeSerializer,
                                FavoriteSerializer)
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from recipes.models import (Favorite, Ingredient, Recipe,
                            IngredientIn, Basket, Tag, Follow)
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from django_filters.rest_framework import DjangoFilterBackend


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class UserView(UserViewSet):
    """Вьюсет юзера."""
    serializer_class = SignUpSerializer

    def get_queryset(self):
        return User.objects.all()


class FollowView(APIView):
    """Вьюсет создания и удаления подписки."""
    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserFollowSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(user=request.user,
                                     author=author).exists():
            return Response(
                {'errors': 'На данного пользователя нет подписки.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=request.user,
                              author=author).delete()
        return Response('Вы отписались', status=status. HTTP_204_NO_CONTENT)


class AllFolowViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет всех подписок."""
    serializer_class = UserFollowGetSerialazer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]

    def perform_create(self, serializer):
        """Добавляем автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.request.method == "GET":
            return RecipeSerializer
        else:
            RecipeCreateSerializer


class BasketAndFavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет общей обработки корзины и избранного."""
    def create(self, request, *args, **kwargs):
        """Создание корзины и избранного."""
        recipe_id = int(self.kwargs['recipes_id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(
            user=request.user, recipe=recipe)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаление объекта из корзины и избранного."""
        recipe_id = self.kwargs['recipes_id']
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id)
        object.delete()
        return Response(status=status. HTTP_204_NO_CONTENT)


class BasketViewSet(BasketAndFavoriteViewSet):
    """
    Вьюсет корзины.
    """
    serializer_class = BasketSerializer
    queryset = Basket.objects.all()
    model = Basket


class FavoriteViewSet(BasketAndFavoriteViewSet):
    """
    Вьюсет избранного.
    """
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite


class DownloadBasket(viewsets.ModelViewSet):
    """
    Сохранение файла списка покупок.
    """
    @action(detail=False)
    def download_basket(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientIn.objects.filter(
            recipe__baskets__user=request.user
        ).values(
            'ingredient__name', 'ingredient__unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="basket.txt"'
        return response
