from django.db import models
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from base.models import BaseModel


@deconstructible
class MediaItemPathValidator(validators.RegexValidator):
    regex = r'^\/[0-9]{4}/[0-9]{4}-[0-9]{2}-[0-9]{2}/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}_[0-9a-z]{8}\.[a-z]{3}$'
    message = _(
        'Enter a valid media item path. Should be like this: `/yyyy/yyyy-mm-dd/yyyy-mm-ddThhmmss_slug.ext`'
    )
    flags = 0


JPG = 'jpg'
PNG = 'png'

MIME_TYPE_CHOICES = (
    (JPG, "image/jpeg"),
    (PNG, "image/png"),
)


class MediaItem(BaseModel):

    media_item_path_validator = MediaItemPathValidator()

    owner = models.ForeignKey(
        get_user_model(),
        help_text=_('User that owns this media item'),
        null=False,
        on_delete=models.CASCADE,
    )

    path = models.CharField(
        _('file path'),
        help_text=_('Required. Path to media item from the root of users archive.'),
        null=False,
        validators=[media_item_path_validator],
        max_length=4096,
    )

    media_type = models.CharField(
        _('mime type'),
        help_text=_('Required. Mime type of the media item. Default: image/jpeg'),
        null=False,
        choices=MIME_TYPE_CHOICES,
        default=[choice[1] if choice[0] == JPG else None for choice in MIME_TYPE_CHOICES][0],
        max_length=64,
    )

    def validate_unique(self, exclude=None):
        o = MediaItem.objects.filter(path=self.path, owner=self.owner)
        if o.exists():
            raise ValidationError({'path': _(
                'There already exists a media item named [%s] for user [%s]' % (self.path, self.owner.username))})

    def __str__(self):
        return self.path

    class Meta:
        db_table = 'media_item'
        unique_together = (
            ('path', 'owner'),
        )
