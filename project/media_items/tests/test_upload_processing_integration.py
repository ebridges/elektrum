import os
import re
import subprocess
from shutil import copyfile
from glob import glob
from urllib.parse import urlparse
from datetime import datetime

import pytest
from assertpy import assert_that

from users.tests.factories import USER_PASSWORD
from media_items.models import MediaItem
from base.tests.util import match_image_key


@pytest.mark.django_db
def test_sign_upload_request_success(authenticated_client, img, env):
    with(env['remote_path']):
        c, u = authenticated_client

        image_key = request_upload(c, img)
        media_id = parse_id_from_key(u.id, image_key)

        remote_file = mock_upload(img['local_path'], env['remote_path'], image_key)
        assert_that(remote_file).exists()

        invoke_processor(image_key)
        actual = MediaItem.objects.get(id=media_id)
        assert_processing(img, actual)


def parse_id_from_key(user_id, key):
    m = match_image_key(str(user_id), key)
    assert m is not None
    image_id = m.group('image_id')
    assert image_id is not None
    return image_id


def assert_processing(e, a):
    assert a is not None
    assert e['aperture'] == a.aperture
    assert a.artist is None
    assert e['camera_make'] == a.camera_make
    assert e['camera_model'] == a.camera_model
    # assert to_date(e['create_date']) == a.create_date
    assert e['create_day_id'] == a.create_day_id
    assert e['file_size'] == a.file_size
    assert e['focal_length_denominator'] == a.focal_length_denominator
    assert e['focal_length_numerator'] == a.focal_length_numerator
    assert e['gps_alt'] == a.gps_alt
    assert e['gps_lat'] == a.gps_lat
    assert e['gps_lon'] == a.gps_lon
    # assert to_date(e['gps_dt']) == a.gps_date_time
    assert e['image_height'] == a.image_height
    assert e['image_width'] == a.image_width
    assert e['iso_speed'] == a.iso_speed
    assert e['mime_type'] == a.mime_type
    assert e['shutter_speed_denominator'] == a.shutter_speed_denominator
    assert e['shutter_speed_numerator'] == a.shutter_speed_numerator
    assert e['shutter_speed'] == a.shutter_speed


def to_date(s):
    formats = [
        '%Y-%m-%d %H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
    ]
    dt = None
    for f in formats:
        try:
            dt = datetime.strptime(s, f)
        except ValueError:
            pass
    return dt


def request_upload(client, img):
    request_url = '/media/request-upload/'
    response = client.post(request_url, {'mime_type': img['mime_type']})
    assert response.status_code == 201
    path = response['Location']
    return urlparse(path).path.lstrip('/')


def mock_upload(local, remote_path, image_key):
    remote_file = '%s/%s' % (remote_path.name, image_key)
    fqpathname = os.path.dirname(remote_file)
    os.makedirs(fqpathname)
    copyfile(local, remote_file)
    return remote_file


def invoke_processor(image_key):
    build_clean_processor()
    run_processor(image_key)


def build_clean_processor():
    cwd = processor_project_dir()
    cmd = ['./gradlew', '--quiet', 'clean', 'fatJar']
    exec_cmd(cwd, cmd)


def run_processor(path):
    cwd = processor_project_dir()
    jar = '%s/build/libs/elektrum-processor*.jar' % cwd
    jar = next(iter(glob(jar)), None)
    assert_that(jar).is_not_none()
    assert_that(jar).exists()
    cmd = [
        'java',
        '-Dlog4j.configurationFile=log4j2.xml',
        '-jar',
        jar,
        '-f',
        path
    ]
    exec_cmd(cwd, cmd)


def exec_cmd(cwd, cmd):
    subprocess.run(
        args=cmd,
        cwd=cwd,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL
    )


def processor_project_dir():
    return os.path.realpath('%s/../processor' % os.getcwd())
