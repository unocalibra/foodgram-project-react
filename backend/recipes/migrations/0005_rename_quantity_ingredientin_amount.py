# Generated by Django 4.2.1 on 2023-06-19 09:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_basket_options_alter_favorite_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientin',
            old_name='quantity',
            new_name='amount',
        ),
    ]