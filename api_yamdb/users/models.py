from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('superuser', 'Суперпользователь'),
)


class MyUser(AbstractUser):
    first_name = models.CharField('Имя', max_length=150)
    email = models.CharField('Электронная почта', max_length=254)
    bio = models.TextField('Биография', blank=True)
    is_staff = models.BooleanField('Персонал', default=False)
    role = models.CharField('Роль', max_length=9, choices=ROLES)
    confirmation_code = models.SmallIntegerField('Код подтверждения',
                                                 blank=True, null=True)

    @property
    def token(self):
        return self._generate_jwt_token()

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

        return token  # .decode('utf-8')
