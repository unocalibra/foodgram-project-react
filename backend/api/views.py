from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filter import IngredientFilter, RecipeFilter
from api.serializers import (BasketSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, SignUpSerializer, TagSerializer,
                             UserFollowGetSerialazer, UserFollowSerializer)
from api.utils import delete_instance, post_instance
from recipes.models import (Basket, Favorite, Follow, Ingredient, IngredientIn,
                            Recipe, Tag)
from users.models import User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]


class UserView(UserViewSet):
    """Вьюсет юзера."""
    serializer_class = SignUpSerializer

    def get_queryset(self):
        return User.objects.all()


class FollowView(APIView):
    """Вьюсет создания и удаления подписки."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        """Создаем подписку."""
        following = get_object_or_404(User, id=user_id)
        data = {'user': request.user.id, 'following': following.id}
        serializer = UserFollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Удаляем подписку."""
        following = get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(user=request.user,
                                     following=following).exists():
            return Response(
                {'errors': 'На данного пользователя нет подписки.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.get(user=request.user,
                           following=following).delete()
        return Response('Вы отписались', status=status. HTTP_204_NO_CONTENT)


class AllFolowViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет всех подписок."""
    serializer_class = UserFollowGetSerialazer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Добавляем автора при создании рецепта."""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.request.method == "GET":
            return RecipeSerializer
        else:
            return RecipeCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientIn.objects.filter(
            recipe__baskets__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="basket.txt"'
        return response

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        """Добавить и удалить в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return post_instance(request, recipe, FavoriteSerializer)
        if request.method == 'DELETE':
            error_message = 'Рецепта нет в избранном!'
            return delete_instance(request, Favorite, recipe, error_message)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавить и удалить в корзину."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return post_instance(request, recipe, BasketSerializer)
        if request.method == 'DELETE':
            error_message = 'Рецепта нет в корзине!'
            return delete_instance(request, Basket, recipe, error_message)
