from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    email = models.CharField(max_length=100)
    bio = models.TextField('Биография', blank=True)
    role = models.TextField('Роль', blank=True)
    confirmation_code = models.SmallIntegerField('Код подтверждения',
                                                 blank=True, null=True)
    is_confirmed = models.BooleanField('Подтвержден', blank=True, null=True)
