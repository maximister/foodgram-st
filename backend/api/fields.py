"""Кастомные типы полей."""
import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField


__all__ = ['Base64ImageField']

# NOTE: вместо него используется Base64ImageField из drf_extra_fields,
# но в условиях было упомянуто,
# что было бы неплохо создать для этих целей свой класс, поэтому оставил


class Base64InternalImageField(serializers.ImageField):
    """Кастомное поле для изображений.

    Упоминалось как nice to do в ТЗ, но не пригодилось.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)
