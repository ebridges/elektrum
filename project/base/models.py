from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class BaseUser(AbstractUser):

  class Meta:
      abstract = True

  id = models.UUIDField(
    _('id'),
    primary_key=True,
    default=uuid4,
    editable=False,
    max_length=64
  )
