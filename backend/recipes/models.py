from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Название', max_length=200, db_index=True)
    unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        """Вернет название ингредиента."""
        return self.name


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    color = ColorField('Цвет', format='hex', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Вернет слаг тега."""
        return self.slug


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(max_length=200)
    tag = models.ManyToManyField(Tag, verbose_name='Тэги')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингредиенты")
    time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1, 'Не должно быть меньше минуты!')])
    description = models.TextField('Описание',
                                   help_text='Введите описание рецепта')
    image = models.ImageField(
        upload_to='recipes/', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        """
        Сортировка по убыванию
        по добавлению.
        """
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Вернет название рецепта."""
        return self.name


class IngredientIn(models.Model):
    """Модель ингредиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientsrecipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientsrecipes'
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Не должно быть меньше 1')]
    )

    class Meta:
        """
        Создание уникальных пар между ингредиентом и рецептом.
        """
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                               name='unique_ingredientin')]

    def __str__(self):
        """Вернет ингредиет в рецепте."""
        return f'{self.ingredient} есть в {self.recipe}'


class TagRecipe(models.Model):
    """Модель тэга рецепта."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        """
        Создание уникальных пар между тэгом и рецептом.
        """
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
        constraints = [models.UniqueConstraint(fields=['tag', 'recipe'],
                                               name='unique_tagrecipe')]

    def __str__(self):
        """Вернет тэг для рецепта."""
        return f'{self.tag} применен для {self.recipe}'


class Basket(models.Model):
    """Модель корзины покупателя."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='baskets')

    class Meta:
        """
        Создание уникальных пар между юзером и рецептом.
        """
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_backet')]

    def __str__(self):
        """Вернет юзера и рецепт."""
        return f'{self.user} добавил в корзину {self.recipe}'


class Follow(models.Model):
    """Модель подписчика."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        """
        Создание уникальных пар между автором и подписчиком.
        """
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_followers'),
        )
        ordering = ["-created"]

    def __str__(self):
        """Вернет информацию о подписке."""
        return f'{self.user} подписался на {self.following}'


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        """
        Создание уникальных пар между юзером и рецептом.
        """
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorite')]

    def __str__(self):
        """Вернет информацию об избранном."""
        return f'{self.user} добавил в избранное {self.recipe}'
