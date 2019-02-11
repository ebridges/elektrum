from pathlib import Path

from django.db import models

from base.models import BaseModel


@deconstructible
class MediaItemPathValidator(validators.RegexValidator):
    regex = r'^\/[0-9]{4}$'
    message = _(
        'Enter a valid media item path. This value may only be a 4 digit year, '
        'with a leading slash.'
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
        null=False,
        help_text=_('User that owns this media item'),
        on_delete=models.CASCADE,
    )

    path = models.CharField(
        _('file path'),
        null=False,
        unique=True,
        help_text=_('Required. Path to media item from the root of your archive.'),
        validators=[media_item_path_validator],
        max_length=4096,
    )

    media_type = models.CharField(
        _('mime type'),
        null=False,
        help_text=_('Required. Mime type of the media item.'),
        choices=MIME_TYPE_CHOICES,
        default=JPG,
        max_length=128,
    )

    image_width = models.IntegerField(
        _('image width'),
        help_text=_('The width dimension of the size of this media image.'),
        null=False,
    )

    image_height = models.IntegerField(
        _('image height'),
        help_text=_('The height dimension of the size of this media image.'),
        null=False,
    )
    file_size = models.IntegerField(
        _('file size'),
        help_text=_('File size in bytes of this media item.'),
        null=False,
    )

    create_date = models.ForeignKey(

    )

    create_time = models.ForeignKey(

    )

    upload_date = models.DateTimeField(

    )

    last_modified = models.DateTimeField(

    )

    camera_make = models.CharField(
        _('camera make'),
        help_text=_('Camera make used for creating this media item.'),
    )

    camera_model = models.CharField(
        _('camera model'),
        help_text=_('Camera model used for creating this media item.'),
    )

    exposure_value = models.IntegerField(
        _('exposure value'),
        help_text=_('EV for the media item.'),
    )

    shutter_speed_denominator = models.IntegerField(
        _('shutter speed denominator'),
        help_text=_('The denominator for the shutter speed for the media item.'),
    )

    shutter_speed_numerator = models.IntegerField(
        _('shutter speed numerator'),
        help_text=_('The numerator for the shutter speed for the media item.'),
    )

    iso_speed = models.IntegerField(
        _('iso speed'),
        help_text=_('The ISO speed for the media item.'),
    )

    focal_length = models.IntegerField(
        _('focal length'),
        help_text=_('The focal length for the media item.'),
    )

    gps_lon = models.FloatField(
        _('gps longitude'),
        help_text=_('Longitudinal value for the GPS location of the media item.')
    )

    gps_lat = models.FloatField(
        _('gps latitude'),
        help_text=_('Latitudinal value for the GPS location of the media item.')
    )

    gps_alt = models.FloatField(
        _('gps altitude'),
        help_text=_('Altitudinal value for the GPS location of the media item.')
    )

    gps_datetime = models.DateTimeField(
        _('gps date'),
        help_text=_('Date & time in UTC of where this media item was created')
    )

    def aperture(self):
        """
        The actual aperture value of lens when the image was taken. Unit is APEX. To convert
        this value to ordinary F-number (F-stop), calculate this value's power of root 2 (=1.4142).
        For example, if the ApertureValue is '5', F-number is 1.4142^5 = F5.6.
        https://en.wikipedia.org/wiki/Exposure_value#EV_and_APEX
        :return:
        """
        # @todo calculate aperture from EV
        return self.exposure_value

    def shutter_speed(self):
        """
        Return the shutter speed from numerator & denominator
        :return:
        """
        return '%s/%s' % (self.shutter_speed_numerator, self.shutter_speed_denominator)

    def gps_loc(self):
        """
        Return the gps location in degrees
        :return:
        """
        # @todo calculate the gps location in degrees/min/sec
        return '%s / %s / %s' % (self.gps_lat, self.gps_lon, self.gps_alt)

    def dimension(self):
        """
        Return the dimension in a standardized form.
        :return:
        """
        return self.image_width, self.image_height

    def dimension_str(self):
        """
        Return the dimension in a standardized form.
        :return:
        """
        return '%sx%s' % self.dimension()

    def filename(self):
        """
        Returns the standard filename for this media item.
        :return:
        """
        return Path(str(self.path)).name

    def archive_location(self):
        """
        Returns the path to this media item within the owner's archive.
        :return:
        """
        return '%s/%s' % (str(self.owner.id), str(self.path))

    def __str__(self):
        return self.path

