from django.db import models
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from base.models import BaseModel


@deconstructible
class CollectionPathValidator(validators.RegexValidator):
  regex = r'^\/[0-9]{4}$'
  message = _(
    'Enter a valid collection path. This value may only be a 4 digit year, '
    'with a leading slash.'
  )
  flags = 0


class Collection(BaseModel):
  collection_path_validator = CollectionPathValidator()

  path = models.CharField(
    _('collection path'),
    help_text=_('Required. Path to media collection from the root of your archive.'),
    validators=[collection_path_validator],
    max_length=1024,
  )

  user = models.ForeignKey(
    get_user_model(),
    null=False, 
    help_text=_('User that owns this collection'),
    on_delete=models.CASCADE,
  )

  def __str__(self):
    return self.path

  def name(self):
    return self.path[1:]


  class Meta:
    db_table = 'collection'
    unique_together = (
      ('path', 'user'),
    )
