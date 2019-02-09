from django.db import models

from base.models import BaseModel
from collection.models import Collection


@deconstructible
class AlbumPathValidator(validators.RegexValidator):
    regex = r'^\/[0-9]{4}-[0-9]{2}-[0-9]{2}$'
    message = _(
        'Enter a valid album path. This value may only be a date in this format: yyyy-mm-dd '
        'with a leading slash.'
    )
    flags = 0


class Album(BaseModel):
    album_path_validator = AlbumPathValidator()

    path = models.CharField(
        _('album path'),
        help_text=_('Required. Path to media album within the album.'),
        validators=[album_path_validator],
        max_length=1024,
    )

    user = models.ForeignKey(
        get_user_model(),
        null=False,
        help_text=_('User that owns this album'),
        on_delete=models.CASCADE,
    )

    collection = models.ForeignKey(
        Collection,
        null=False,
        help_text=_('Collection this album is part of'),
        on_delete=models.CASCADE,
    )

    def validate_unique(self, exclude=None):
        o = Album.objects.filter(path=self.path, user=self.user)
        if o.exists():
            raise ValidationError({'path': _(
                'There exists already a path with name [%s] for user [%s]' % (self.path, self.user.username))})

    def __str__(self):
        return self.path

    def name(self):
        return self.path[1:]

    class Meta:
        db_table = 'album'
        unique_together = (
            ('path', 'user'),
        )
