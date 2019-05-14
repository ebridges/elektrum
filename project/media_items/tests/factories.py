from datetime import date, datetime, timezone
import random
from uuid import uuid4

import pytest
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyNaiveDateTime, FuzzyText
from factory import Sequence, SubFactory, LazyAttribute, SelfAttribute, LazyFunction
from pytest_factoryboy import register

from media_items.models import MediaItem
from users.tests.factories import UserFactory
from date_dimension.tests.factories import DateDimensionFactory


class MediaItemFactory(DjangoModelFactory):
    class Meta:
        model = MediaItem

    id = LazyFunction(uuid4)
    owner = SubFactory(UserFactory)
    file_path = LazyAttribute(lambda o: '/%s/%s.jpg' % (o.owner.id, o.id))
    mime_type = 'image/jpeg'
    create_day = SubFactory(DateDimensionFactory)
    create_date = LazyAttribute(lambda o: datetime(year=o.create_day.year,
                                month=o.create_day.month,
                                day=o.create_day.day))
    file_size = random.randint(1000, 100000)
    image_width = random.randint(128,4096)
    image_height = random.randint(128,4096)
    camera_make = FuzzyText(prefix='camera-make.')
    camera_model = FuzzyText(prefix='camera-model.')
    aperture = FuzzyText(prefix='aperture.', length=3)
    shutter_speed_numerator = 1
    shutter_speed_denominator = random.randint(8,128)
    shutter_speed = '%s/%s' % (shutter_speed_numerator, shutter_speed_denominator)
    focal_length_numerator = 1
    focal_length_denominator = random.randint(8,128)
    iso_speed = random.randint(10,500)
    gps_lon = random.randint(-180, 180)
    gps_lat = random.randint(-90, 90)
    gps_alt = random.randint(0, 10000)
    gps_date_time = LazyAttribute(lambda o: datetime(year=o.create_date.year,
                                  month=o.create_date.month,
                                  day=o.create_date.day,
                                  tzinfo=timezone.utc))
    artist = LazyAttribute(lambda o: o.owner.username)


register(MediaItemFactory)
