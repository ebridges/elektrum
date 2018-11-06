from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(blank=False, null=False, unique=True, max_length=512, verbose_name='email address')
    first_name = models.CharField(blank=False, null=False, max_length=255, verbose_name='first name')
    last_name = models.CharField(blank=False, null=False, max_length=255, verbose_name='last name')

    def __str__(self):
        return self.email
