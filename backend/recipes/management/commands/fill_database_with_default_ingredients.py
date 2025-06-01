"""Скрипт для наполнения базы ингредиентов дефолтными значениями."""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для наполнения базы ингредиентов дефолтными значениями \
        из csv-файла."""

    help = 'Загрузить список дефолтных ингредиентов из CSV файла'

    def add_arguments(self, parser):
        """Парсинг аргументов из командной строки."""
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к CSV файлу c ингредиентами',
            required=False
        )

    def handle(self, *args, **options):
        """Перекладывание csv в бд."""
        csv_path = options.get('path')

        if csv_path:
            base_dir = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(settings.BASE_DIR))))
            csv_file = os.path.join(base_dir, 'foodgram-st', csv_path)
        else:
            data_dir = os.path.join(settings.BASE_DIR, '..', 'data')
            csv_file = os.path.join(data_dir, 'ingredients.csv')

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(
                f'Файл {csv_file} не найден')
            )
            return

        Ingredient.objects.all().delete()

        ingredients_count = 0

        try:
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

            success_message = (
                f'Успешно загружено {ingredients_count} ингредиентов '
                f'из файла {csv_file}'
            )
            self.stdout.write(self.style.SUCCESS(success_message))
        except Exception as e:
            raise CommandError(f'Ошибка при чтении файла: {e}')
