from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, TagViewSet, UserView, AllFolowViewSet,
                    FollowView, FavoriteViewSet, BasketViewSet, RecipeViewSet)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', UserView, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/follows/', AllFolowViewSet.as_view({'get': 'list'}),
         name='follows'),
    path('users/<user_id>/follow/', FollowView.as_view(),
         name='follow'),
    path('', include(router.urls)),
    path('recipes/<recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/<recipes_id>/basket/',
         BasketViewSet.as_view({'post': 'create',
                                'delete': 'delete'}), name='basket'),
    path('auth/', include('djoser.urls.authtoken')),
]
