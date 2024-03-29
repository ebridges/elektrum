from uuid import uuid4

from django.db import models
from django.db.models import Field
from django.utils.translation import gettext_lazy as _


class DateTimeNoTZField(Field):
    def db_type(self, connection):
        return 'TIMESTAMP WITHOUT TIME ZONE'


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(_('id'), primary_key=True, default=uuid4, editable=False, max_length=64)
