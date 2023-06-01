from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Настройка конфигурации приложения Api.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Управление Api сайта'
