from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Настройка конфигурации приложения Users.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Управление юзерами'
