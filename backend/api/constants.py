"""Константы для пагинации."""
from django.conf import settings

PAGE_SIZE = getattr(settings, 'PAGE_SIZE', 6)
PAGE_SIZE_PARAM = 'limit'
MAX_PAGE_SIZE = 100
