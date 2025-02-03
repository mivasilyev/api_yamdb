from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from api_yamdb.constants import (
    VALID_USERNAME_PATTERN, FORBIDDEN_NAME, MAX_LENTH,
    LENG_DATA_USER,)


class UsernameRegexValidator(UnicodeUsernameValidator):
    """Валидация имени пользователя."""

    regex = VALID_USERNAME_PATTERN
    flags = 0
    max_length = LENG_DATA_USER
    message = ('Введите правильное имя пользователя. Оно может содержать'
               ' только буквы, цифры и знаки @/./+/-/_.'
               f' Длина не более {LENG_DATA_USER} символов')
    error_messages = {
        'invalid': f'Набор символов не более {LENG_DATA_USER}. '
                   'Только буквы, цифры и @/./+/-/_',
        'required': 'Поле не может быть пустым',
    }


def username_test(value):
    """Проверка имени пользователя (me недопустимое имя)."""
    if value == FORBIDDEN_NAME:
        raise ValidationError(
            f'Имя пользователя {FORBIDDEN_NAME} не разрешено.'
        )
    if len(value) > MAX_LENTH:
        raise ValidationError(
            'Имя пользователя слишком длинное.'
        )
    return value
