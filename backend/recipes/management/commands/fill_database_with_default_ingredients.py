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
        try:
            csv_path = options.get('path')

            if csv_path:
                base_dir = os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.dirname(settings.BASE_DIR))))
                csv_file = os.path.join(base_dir, 'foodgram-st', csv_path)
            else:
                data_dir = os.path.join(settings.BASE_DIR, '..', 'data')
                csv_file = os.path.join(data_dir, 'ingredients.csv')

            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                created = Ingredient.objects.bulk_create(
                    [
                        Ingredient(
                            name=row[0].strip(),
                            measurement_unit=row[1].strip()
                        )
                        for row in reader if len(row) == 2
                    ],
                    ignore_conflicts=True
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно загружено ингредиентов: {len(created)}.'
                )
            )
        except Exception as e:
            raise CommandError(f'Ошибка при чтении файла {csv_file}: {e}')
