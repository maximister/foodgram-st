"""Скрипт для наполнения базы ингредиентов дефолтными значениями из JSON."""
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для наполнения базы ингредиентов дефолтными значениями \
        из json-файла."""

    help = 'Загрузить список дефолтных ингредиентов из JSON файла'

    def add_arguments(self, parser):
        """Парсинг аргументов из командной строки."""
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к JSON файлу c ингредиентами',
            required=False
        )

    def handle(self, *args, **options):
        """Перекладывание json в бд."""
        try:
            json_path = options.get('path')

            if json_path:
                base_dir = os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.dirname(settings.BASE_DIR))))
                json_file = os.path.join(base_dir, 'foodgram-st', json_path)
            else:
                data_dir = os.path.join(settings.BASE_DIR, '..', 'data')
                json_file = os.path.join(data_dir, 'ingredients.json')

            with open(json_file, 'r', encoding='utf-8') as file:
                ingredients_data = json.load(file)
                created = Ingredient.objects.bulk_create(
                    [
                        Ingredient(
                            name=item['name'].strip(),
                            measurement_unit=item['measurement_unit'].strip()
                        )
                        for item in ingredients_data
                    ],
                    ignore_conflicts=True
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно загружено ингредиентов из JSON: {len(created)}.'
                )
            )
        except Exception as e:
            raise CommandError(f'Ошибка при чтении файла {json_file}: {e}')
