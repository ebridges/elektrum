from django.db import models
from django.db.models.base import Model
from django.utils.translation import gettext_lazy as _


class DateDimension(Model):
    yyyymmdd = models.IntegerField(
        _('This date as an integer'),
        help_text=_('Required. YYYYMMDD as an integer.'),
        null=False,
        primary_key=True,
    )

    iso_date = models.CharField(
        _('This date formatted as an ISO date (i.e. yyyy-mm-dd)'),
        help_text=_('Required. YYYY-MM-DD as a string.'),
        null=False,
        max_length=16,
    )

    this_date = models.DateField(
        _('This date as a typed date field.'),
        help_text=_('Required. This date as a date-type.'),
        null=False,
    )

    year = models.IntegerField(
        _('Year of this date.'),
        help_text=_('Required. The year of this date as an integer.'),
        null=False,
    )

    month = models.IntegerField(
        _('Month of this date.'),
        help_text=_('Required. The month of this date as an integer.'),
        null=False,
    )

    day = models.IntegerField(
        _('Day of this date.'),
        help_text=_('Required. The day of this date as an integer.'),
        null=False,
    )

    week_num = models.IntegerField(
        _('Week number.'),
        help_text=_('Required. Number of the week in the year this date falls in.  The first week of a year is the '
                    'first calendar week of the year containing a Thursday.'),
        null=False,
    )

    week_day = models.IntegerField(
        _('Day of the week.'),
        help_text=_('Required. Number of the day in the week of this date. 1 == Monday, 7 == Sunday'),
        null=False,
    )

    day_in_year = models.IntegerField(
        _('Day in the year.'),
        help_text=_('Required. Ordinal count of day in the year. From 1-36[56]'),
        null=False,
    )

    class Meta:
        db_table = 'date_dim'
