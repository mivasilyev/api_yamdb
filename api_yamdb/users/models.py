from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import EMAIL_MAX_LENGTH

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class MyUser(AbstractUser):
    email = models.CharField(
        'Электронная почта', max_length=EMAIL_MAX_LENGTH, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Роль', max_length=9,
                            choices=ROLES, default=USER)
    confirmation_code = models.SmallIntegerField('Код подтверждения',
                                                 blank=True, null=True)

    def _generate_jwt_token(self):
        """Создаем JWT-Token с экспирацией через 60 дней."""
        import jwt
        from datetime import datetime, timedelta
        from django.conf import settings
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_superuser is True
                or self.is_staff is True)

    @property
    def is_moderator(self):
        return self.role == MODERATOR
