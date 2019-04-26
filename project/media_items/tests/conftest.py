from users.tests.factories import *
import pytest
import os

from tempfile import TemporaryDirectory


@pytest.fixture(name='img')
def image_info():
    return {
        'aperture': 'f/1.8',
        'artist': None,
        'camera_make': 'Google',
        'camera_model': 'Pixel 3',
        'create_date': '2019-04-13 19:29:12',
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
def get_db_connect_info(live_server):
    db_name = live_server._live_server_modified_settings.wrapped.DATABASES['default']['NAME']
    db_host = live_server._live_server_modified_settings.wrapped.DATABASES['default']['HOST']
    db_port = live_server._live_server_modified_settings.wrapped.DATABASES['default']['PORT']
    db_user = live_server._live_server_modified_settings.wrapped.DATABASES['default']['USER']
    db_pass = live_server._live_server_modified_settings.wrapped.DATABASES['default']['PASSWORD']

    bucket_name = 'my-mock-bucket'
    remote_path = TemporaryDirectory(suffix='.%s' % bucket_name)

    # used by upload url request
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = bucket_name

    # used by image processor
    os.environ['DB_JDBC_URL'] = 'jdbc:postgresql://%s:%s/%s' % (db_host, db_port, db_name)
    os.environ['DB_USERNAME'] = db_user
    os.environ['DB_PASSWORD'] = db_pass
    os.environ['IMAGE_ROOT'] = remote_path.name

    return {
        'bucket_name': bucket_name,
        'remote_path': remote_path
    }
