import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Класс настройки команды для импорта в базу из файла.
    python manage.py load_import
    """
    help = 'Импорт из файла в базу данных.'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data/ingredients.csv'),
                  'rt', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    unit=row[1]
                )
