from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from base.models import BaseModel, DateTimeNoTZField
from media_items.models import MediaItem
from enum import Enum, unique
from uuid import uuid4


@unique
class ShareState(str, Enum):
    INITIAL = 'initial'
    DRAFT = 'draft'
    SHARED = 'shared'

    def describe(self):
        return self.value, self.value.capitalize()


class Share(BaseModel):
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Share, self).save(*args, **kwargs)

    created = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=512, blank=True, null=True)
    message = models.TextField(max_length=2048, blank=True, null=True)
    state = models.CharField(
        default=ShareState.INITIAL,
        choices=[state.describe() for state in list(ShareState)],
        max_length=24,
    )
    shared_on = DateTimeNoTZField(
        _('share date'), help_text=_('The date and time these media items were shared.'), null=True
    )
    shared_by = models.ForeignKey(
        get_user_model(), blank=False, null=False, on_delete=models.CASCADE
    )
    shared_to = models.ManyToManyField('Audience', through='AudienceShare')
    shared = models.ManyToManyField(MediaItem, through='MediaShare')

    def to_count(self):
        return len(self.shared_to.filter(unsubscribed=False))

    def shared_count(self):
        return len(self.shared.all())

    def from_data(self, data, shared_on=lambda: None):
        user = get_user_model().objects.get(pk=data['from_id'])
        self.message = data['share_message']
        self.subject = data['subject_line']
        self.shared_by = user
        self.shared_to.clear()
        for address in data['to_address']:
            (audience, created) = Audience.objects.get_or_create(email=address, shared_by=user)
            self.shared_to.add(audience)
        self.shared_on = shared_on()

    def view(self):
        return {
            'created': self.created,
            'modified': self.modified,
            'to': {
                audience.email: audience.id
                for audience in self.shared_to.filter(unsubscribed=False)
            },
            'owner_id': self.shared_by.id,
            'shared_by': self.shared_by.name(),
            'from': self.shared_by.email,
            'subject': self.subject,
            'message': self.message,
            'shared_on': self.shared_on,
            'state': self.state,
            'shared': [item.view() for item in self.shared.all()],
            'shared_count': self.shared_count(),
            'to_count': self.to_count(),
        }


class Audience(BaseModel):
    class Meta:
        unique_together = [['email', 'shared_by']]

    email = models.EmailField(blank=False, null=False, max_length=512)
    shared_by = models.ForeignKey(
        get_user_model(), blank=False, null=True, on_delete=models.CASCADE
    )
    unsubscribed = models.BooleanField(
        null=False,
        default=False,
        verbose_name=_(
            'Whether this email\'s owner has requested to be unsubscribed for this user.'
        ),
    )


class AudienceShare(models.Model):
    share = models.ForeignKey(Share, models.CASCADE)
    shared_to = models.ForeignKey(Audience, models.CASCADE)


class MediaShare(models.Model):
    share = models.ForeignKey(Share, models.CASCADE)
    shared_media = models.ForeignKey(MediaItem, models.CASCADE)
