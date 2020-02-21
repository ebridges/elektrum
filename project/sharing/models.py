from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel, DateTimeNoTZField
from media_items.models import MediaItem
from users.models import CustomUser


class Audience(BaseModel):
    email = models.EmailField(
        blank=False, null=False, unique=True, max_length=512, verbose_name='email address'
    )
    shares = models.ManyToManyField(
        'media_items.MediaItem', through='Share', related_name='shared_on'
    )


class Share(BaseModel):
    publisher = models.ForeignKey(CustomUser, related_name='publisher', on_delete=models.CASCADE)
    audience = models.ForeignKey(Audience, related_name='audience', on_delete=models.CASCADE)
    media_items = models.ForeignKey(
        MediaItem, related_name='shared_media', on_delete=models.CASCADE
    )
    state = models.CharField(default=10, choices=[(10, 'draft'), (30, 'shared')], max_length=24)
    share_date = DateTimeNoTZField(
        _('share date'),
        help_text=_('Required. The date and time these media items were shared.'),
        null=True,
    )
