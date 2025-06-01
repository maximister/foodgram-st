import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает список ингредиентов из CSV файла'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, '..', 'data')
        csv_file = os.path.join(data_dir, 'ingredients.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(
                f'Файл {csv_file} не найден')
            )
            return
            
        Ingredient.objects.all().delete()
        
        ingredients_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    name, measurement_unit = row
                    Ingredient.objects.create(
                        name=name.strip(),
                        measurement_unit=measurement_unit.strip()
                    )
                    ingredients_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Успешно загружено {ingredients_count} ингредиентов')
        )
