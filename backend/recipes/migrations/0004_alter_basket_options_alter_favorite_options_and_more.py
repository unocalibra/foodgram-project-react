# Generated by Django 4.2.1 on 2023-06-05 07:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_tagrecipe_follow_favorite_basket_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basket',
            options={'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredientin',
            options={'verbose_name': 'Ингредиент рецепта', 'verbose_name_plural': 'Ингредиенты в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='tagrecipe',
            options={'verbose_name': 'Тэг рецепта', 'verbose_name_plural': 'Тэги рецепта'},
        ),
    ]