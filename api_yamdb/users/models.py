from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import LENG_EMAIL, ROLE_MAX_LENTH

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class ProjectUser(AbstractUser):
    email = models.CharField(
        'Электронная почта', max_length=LENG_EMAIL, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Роль', max_length=ROLE_MAX_LENTH,
                            choices=ROLES, default=USER)
    confirmation_code = models.SmallIntegerField('Код подтверждения',
                                                 blank=True, null=True)

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR
