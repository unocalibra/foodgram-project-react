from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс для Юзера."""
    username = models.CharField(max_length=150, db_index=True, unique=True)
    email = models.EmailField(max_length=254, db_index=True, unique=True)
    name = models.TextField(max_length=254)
    last_name = models.TextField(max_length=254)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'email', 'name', 'last_name']

    class Meta:
        """Сортировка по id."""
        ordering = ['id']

    def __str__(self):
        """Вернет имя пользователя."""
        return self.username
