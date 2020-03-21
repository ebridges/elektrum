from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel, DateTimeNoTZField
from media_items.models import MediaItem
from users.models import CustomUser


class Share(BaseModel):
    state = models.CharField(
        default=10, choices=[(10, 'initial'), (20, 'draft'), (30, 'shared')], max_length=24
    )
    shared_on = DateTimeNoTZField(
        _('share date'), help_text=_('The date and time these media items were shared.'), null=True
    )
    shared_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shared_to = models.ManyToManyField('Audience', through='AudienceShare')
    shared = models.ManyToManyField(MediaItem, through='MediaShare')


class Audience(BaseModel):
    email = models.EmailField(blank=False, null=False, unique=True, max_length=512)


class AudienceShare(models.Model):
    share = models.ForeignKey(Share, models.CASCADE)
    shared_to = models.ForeignKey(Audience, models.CASCADE)


class MediaShare(models.Model):
    share = models.ForeignKey(Share, models.CASCADE)
    shared_media = models.ForeignKey(MediaItem, models.CASCADE)
