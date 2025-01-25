from django.core.exceptions import ValidationError
from django.utils.timezone import now


def current_year(value):
    """Значение поля не должно быть больше текущего года."""
    if value > now().year:
        raise ValidationError('Этот год ещё не наступил!')
    if value < 0:
        raise ValidationError('Год не может быть отрицательным!')
