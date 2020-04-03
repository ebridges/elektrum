from os.path import basename
from django.db import models
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

# from django.contrib.gis.db import models

from base.models import BaseModel, DateTimeNoTZField
from date_dimension.models import DateDimension
from base.views.utils import media_url


@deconstructible
class MediaItemPathValidator(validators.RegexValidator):
    regex = r'^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}/[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}\.[a-z]{3}$'
    message = _('Enter a valid media item path. Should be like this: `uuid/uuid.ext`')
    flags = 0


JPG = 'jpg'
PNG = 'png'

MIME_TYPE_CHOICES = ((JPG, 'image/jpeg'), (PNG, 'image/png'))
MIME_TYPE_EXTENSIONS = {'image/jpeg': JPG, 'image/png': PNG}


class MediaItem(BaseModel):

    media_item_path_validator = MediaItemPathValidator()

    owner = models.ForeignKey(
        get_user_model(),
        help_text=_('User that owns this media item'),
        null=False,
        on_delete=models.CASCADE,
    )

    file_path = models.CharField(
        _('file path'),
        help_text=_('Required. Path to media item from the root of users archive.'),
        null=False,
        validators=[media_item_path_validator],
        max_length=4096,
    )

    mime_type = models.CharField(
        _('mime type'),
        help_text=_('Required. Mime type of the media item. Default: image/jpeg'),
        null=False,
        choices=MIME_TYPE_CHOICES,
        default=[choice[1] if choice[0] == JPG else None for choice in MIME_TYPE_CHOICES][0],
        max_length=64,
    )

    create_date = DateTimeNoTZField(
        _('create date'),
        help_text=_('Required. The date and time this media item was created.'),
        null=False,
    )

    create_day = models.ForeignKey(
        DateDimension,
        help_text=_('The date the media item was created.'),
        on_delete=models.DO_NOTHING,
        null=False,
    )

    file_size = models.BigIntegerField(
        _('file size'), help_text=_('Required. The size in bytes of the media item.'), null=False
    )

    image_width = models.IntegerField(
        _('image width'), help_text=_('Required. The width of this media item.'), null=False
    )

    image_height = models.IntegerField(
        _('image height'), help_text=_('Required. The height of this media item.'), null=False
    )

    camera_make = models.CharField(
        _('camera make'),
        help_text=_('Optional. Name of the camera used for creating this media item.'),
        null=True,
        max_length=64,
    )

    camera_model = models.CharField(
        _('camera model'),
        help_text=_('Optional. Model of the camera used for creating this media item.'),
        null=True,
        max_length=64,
    )

    aperture = models.CharField(
        _('aperture'),
        help_text=_('Optional. The lens aperture setting used when this media item was created.'),
        null=True,
        max_length=64,
    )

    shutter_speed_numerator = models.IntegerField(
        _('shutter speed (numerator)'),
        help_text=_(
            'Optional. The shutter speed (numerator) setting used when this media item was created.'
        ),
        null=True,
    )

    shutter_speed_denominator = models.IntegerField(
        _('shutter speed (denominator)'),
        help_text=_(
            'Optional. The shutter speed (denominator) setting used when this media item was created.'
        ),
        null=True,
    )

    shutter_speed = models.CharField(
        _('shutter speed'),
        help_text=_('Optional. The shutter speed setting used when this media item was created.'),
        null=True,
        max_length=16,
    )

    focal_length_numerator = models.IntegerField(
        _('focal length (numerator)'),
        help_text=_(
            'Optional. The focal length (numerator) setting used when this media item was created.'
        ),
        null=True,
    )

    focal_length_denominator = models.IntegerField(
        _('focal length (denominator)'),
        help_text=_(
            'Optional. The focal length (denominator) setting used when this media item was created.'
        ),
        null=True,
    )

    iso_speed = models.IntegerField(
        _('iso speed'),
        help_text=_('Optional. The ISO speed of the exposure used to create this media item.'),
        null=True,
    )

    gps_lon = models.FloatField(
        _('gps longitude'),
        help_text=_(
            'Optional. The longitude of the GPS location of where this media item was created.'
        ),
        null=True,
    )

    gps_lat = models.FloatField(
        _('gps latitude'),
        help_text=_(
            'Optional. The latitude of the GPS location of where this media item was created.'
        ),
        null=True,
    )

    gps_alt = models.FloatField(
        _('gps altitude'),
        help_text=_(
            'Optional. The altitude of the GPS location of where this media item was created.'
        ),
        null=True,
    )

    gps_date_time = models.DateTimeField(
        _('gps date time'),
        help_text=_(
            'Optional. The date and time in UTC at the GPS location of where this media item was created.'
        ),
        null=True,
    )

    # gps_location = models.PointField(
    #     _('gps coordinate'),
    #     help_text=_('Optional. The coordinate for the GPS location of where this media item was created.'),
    #     null=True,
    #     dim=3
    # )

    artist = models.CharField(
        _('artist'),
        help_text=_('Optional. Artist responsible for creating this media item.'),
        null=True,
        max_length=64,
    )

    def save(self, *args, **kwargs):
        created = int(self.create_date.strftime('%Y%m%d'))
        self.create_day = DateDimension.objects.get(yyyymmdd=created)
        super(MediaItem, self).save(*args, **kwargs)

    def view(self):
        return {
            'media_item': self,
            'item_id': self.id,
            'file_name': self.create_day_id,
            'url': media_url(self.file_path),
            'media_item_url': media_url(self.file_path),
            'file_path': self.file_path,
            'title': self.create_date,
            'collection_year': self.create_day.year,
            'album_id': self.create_day.iso_date,
            'yyyymmdd': self.yyyy_mm_dd(),
            'year': int(str(self.create_day_id)[:4]),
            'basename': basename(self.file_path),
            'owner_id': owner.id,
            'media_ext': MIME_TYPE_EXTENSIONS[self.mime_type],
        }

    def yyyy_mm_dd(self):
        val = str(self.create_day_id)
        return '%s-%s-%s' % (val[0:4], val[4:6], val[6:8])

    def __str__(self):
        return self.file_path

    class Meta:
        db_table = 'media_item'
