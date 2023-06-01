from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # Главная страница
    path('', views.index),
]
