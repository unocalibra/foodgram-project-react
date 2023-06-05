from django.contrib import admin

from users.models import User
from .models import (Ingredient,
                     Tag,
                     Recipe,
                     Favorite,
                     IngredientIn,
                     Basket,
                     Follow,
                     TagRecipe)


class IngredientInInline(admin.TabularInline):
    """
    Настройка отображения модели-вставки IngredientIn
    без дополнительных форм extra.
    """
    model = IngredientIn
    extra = 0


class TagRecipeInline(admin.TabularInline):
    """
    Настройка отображения модели-вставки TagRecipe
    без дополнительных форм extra.
    """
    model = TagRecipe
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели User в интерфейсе админки.
    """
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Ingredient в интерфейсе админки.
    """
    list_display = ('name', 'unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Tag в интерфейсе админки.
    """
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Recipe в интерфейсе админки.
    """
    list_display = ('id', 'name', 'author', 'count_in_fav')
    search_fields = ('name', 'author', 'tag',)
    list_filter = ('name', 'author', 'tag',)
    empty_value_display = '-empty-'
    inlines = (IngredientInInline, TagRecipeInline,)

    def count_in_fav(self, obj):
        """"Счетчик кол-ва добавлений в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Favorite в интерфейсе админки.
    """
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-empty-'


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Basket в интерфейсе админки.
    """
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-empty-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Follow в интерфейсе админки.
    """
    list_display = ('user', 'following')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-empty-'
