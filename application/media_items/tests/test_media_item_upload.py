from os import environ, path, makedirs, stat
import subprocess
import tempfile
from shutil import copyfile
from urllib.parse import urlparse
from datetime import datetime

from django.shortcuts import reverse

import pytest
from assertpy import assert_that

from media_items.models import MediaItem
from base.tests.util import match_image_key
from elektrum.deploy_util import download_github_release
from elektrum.deploy.task_actions import ELEKTRUM_PROCESSOR_VERSION


@pytest.mark.django_db
def test_sign_upload_request_success(authenticated_client, img, env):
    with env['remote_path']:
        c, u = authenticated_client

        image_key = upload_request(c, img)
        media_id = parse_id_from_key(u.id, image_key)
        assert_that(media_id).is_not_none()

        remote_file = mock_upload(img['local_path'], env['remote_path'], image_key)
        assert_that(remote_file).exists()

        version = ELEKTRUM_PROCESSOR_VERSION['development']
        invoke_processor(image_key, version)
        actual = MediaItem.objects.get(file_path=image_key)
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
    # assert to_date(e['gps_dt']) == a.gps_date_time
    assert_that(e['gps_lat']).is_close_to(a.gps_lat, 0.001)
    assert_that(e['gps_lon']).is_close_to(a.gps_lon, 0.001)
    assert e['image_height'] == a.image_height
    assert e['image_width'] == a.image_width
    assert e['iso_speed'] == a.iso_speed
    assert e['mime_type'] == a.mime_type
    assert e['shutter_speed_denominator'] == a.shutter_speed_denominator
    assert e['shutter_speed_numerator'] == a.shutter_speed_numerator
    assert e['shutter_speed'] == a.shutter_speed


def to_date(s):
    formats = ['%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S']
    dt = None
    for f in formats:
        try:
            dt = datetime.strptime(s, f)
        except ValueError:
            pass
    return dt


def upload_request(client, img):
    url = reverse('upload-request')
    response = client.post(url, {'mime_type': img['mime_type']})
    assert response.status_code == 201
    path = response['Location']
    return urlparse(path).path.lstrip('/')


def mock_upload(local, remote_path, image_key):
    remote_file = '%s/%s' % (remote_path.name, image_key)
    fqpathname = path.dirname(remote_file)
    makedirs(fqpathname)
    copyfile(local, remote_file)
    return remote_file


def invoke_processor(image_key, version):
    assert_that(image_key).is_not_none()
    with tempfile.NamedTemporaryFile(prefix='elektrum-processor', suffix='.jar') as temp:
        token = environ['GITHUB_TOKEN']
        if not token:
            raise ValueError('unable to locate GITHUB_TOKEN in environment')

        content_type = 'application/java-archive'
        download_github_release(
            token, 'ebridges/elektrum-processor', version, temp.name, content_type
        )
        assert_that(temp.name).exists() and assert_that(stat(temp.name).st_size).is_positive()

        cmd = ['java', '-Dlog4j.configurationFile=log4j2.xml', '-jar', temp.name, '-f', image_key]
        subprocess.run(args=cmd, stderr=subprocess.STDOUT)
