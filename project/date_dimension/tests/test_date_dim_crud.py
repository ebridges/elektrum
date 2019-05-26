from datetime import date
from date_dimension.models import DateDimension
import pytest


@pytest.mark.django_db
def test_date_dim_create():
    d = date(2001, 9, 11)
    dd = DateDimension.create_from(d)
    assert dd is not None
    assert dd.this_date == d
    assert dd.yyyymmdd == 20010911
    assert dd.iso_date == '2001-09-11'
    assert dd.year == 2001
    assert dd.month == 9
    assert dd.day == 11
    assert dd.week_num == 37
    assert dd.week_day == 2
    assert dd.day_in_year == 254


@pytest.mark.django_db
def test_dim_create_from_factory(date_dimension_factory):
    d = date(2001, 9, 11)
    dd = date_dimension_factory(from_date=d)
    assert dd is not None
    assert dd.this_date == d
    assert dd.yyyymmdd == 20010911
    assert dd.iso_date == '2001-09-11'
    assert dd.year == 2001
    assert dd.month == 9
    assert dd.day == 11
    assert dd.week_num == 37
    assert dd.week_day == 2
    assert dd.day_in_year == 254
