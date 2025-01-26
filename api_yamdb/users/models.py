from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    first_name = models.CharField(max_length=150)
    email = models.CharField(max_length=100)
    bio = models.TextField('Биография', blank=True)
    role = models.TextField('Роль', blank=True)
    confirmation_code = models.SmallIntegerField('Код подтверждения',
                                                 blank=True, null=True)
    is_confirmed = models.BooleanField('Подтвержден', blank=True, null=True)

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
