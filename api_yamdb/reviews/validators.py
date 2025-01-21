from django.core.exceptions import ValidationError
from django.utils.timezone import now


def current_year(value):
    """Значение поля не должно быть больше текущего года."""
    if value > now().year:
        raise ValidationError('Такой год ещё не наступил!')
