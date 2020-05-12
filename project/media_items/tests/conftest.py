from datetime import date

from users.tests.factories import *
from media_items.tests.factories import *
from date_dimension.tests.factories import *

import pytest

from tempfile import TemporaryDirectory

from assertpy import assert_that
from os import getenv


@pytest.fixture
def media_items(custom_user, count_shared=5, count_shared_to=5):
    date_dimension = DateDimensionFactory(from_date=date(1950, 9, 11))
    media_items = MediaItemFactory.create_batch(
        size=count_shared, owner=custom_user, create_day=date_dimension
    )
    return media_items


@pytest.fixture(name='img')
def image_info():
    return {
        'aperture': 'f/1.8',
        'artist': None,
        'camera_make': 'Google',
        'camera_model': 'Pixel 3',
        'create_date': '2019-04-13 23:28:47',
        'create_day_id': 20190413,
        'file_size': 1494846,
        'focal_length_denominator': 1000,
        'focal_length_numerator': 4440,
        'gps_alt': 9.3,
        'gps_dt': '2019-04-13 23:28:47+00:00',
        'gps_lat': 40.7194888888889,
        'gps_lon': -73.9642972222222,
        'image_height': 3024,
        'image_width': 4032,
        'iso_speed': 55,
        'local_path': 'media_items/tests/resources/test-file-upload.jpg',
        'mime_type': 'image/jpeg',
        'shutter_speed_denominator': 100,
        'shutter_speed_numerator': 783,
        'shutter_speed': '1/227 sec',
    }


@pytest.fixture(name='env')
def get_db_connect_info(live_server, monkeypatch):
    # noinspection PyProtectedMember
    database_name = live_server._live_server_modified_settings.wrapped.DATABASES['default']['TEST'][
        'NAME'
    ]

    # bucket name is used to disable some tests in the Java processing code
    bucket_name = 'processing-integration-test'
    remote_path = TemporaryDirectory(suffix='.%s' % bucket_name)
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'XXXX22XXXXXX4XX2XXXX')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', '0AbbbCtSAfgpoi71w8WERw8AviFYatdIV3xcPGry')

    # used by upload url request & image processor
    monkeypatch.setenv('AWS_UPLOAD_BUCKET_NAME', bucket_name)

    # used by image processor
    if getenv('DB_USERNAME'):
        del os.environ['DB_USERNAME']  # force processor into 'test' db mode

    db_url = 'jdbc:sqlite:%s' % database_name
    monkeypatch.setenv('DB_JDBC_URL', db_url)
    monkeypatch.setenv('IMAGE_ROOT', remote_path.name)

    assert_that(getenv('DB_USERNAME')).is_none()
    assert_that(getenv('DB_JDBC_URL')).is_equal_to(db_url)
    assert_that(getenv('IMAGE_ROOT')).is_equal_to(remote_path.name)

    return {'bucket_name': bucket_name, 'remote_path': remote_path}
