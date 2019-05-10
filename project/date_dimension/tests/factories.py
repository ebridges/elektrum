from datetime import date, datetime, timezone

import pytest
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDate
from pytest_factoryboy import register

from date_dimension.models import DateDimension


class DateDimensionFactory(DjangoModelFactory):
    class Meta:
        model = DateDimension

    this_date = FuzzyDate(start_date=date(2010, 2, 26)).fuzz()
    yyyymmdd = int(this_date.strftime('%Y%m%d'))
    year = this_date.year
    month = this_date.month
    day = this_date.day
    week_num = this_date.isocalendar()[1]
    week_day = this_date.isoweekday()
    day_in_year = this_date.timetuple().tm_yday


register(DateDimensionFactory)
