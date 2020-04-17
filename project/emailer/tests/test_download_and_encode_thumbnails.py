from base64 import b64decode, b64encode
from datetime import date
from os.path import exists, isfile
from os import access, R_OK, getcwd
from shutil import copyfile
from tempfile import NamedTemporaryFile

import pytest
from PIL import Image

import emailer
from emailer.utils import download_and_encode_thumbnails
from emailer.views import THUMBNAIL_DIMS


SAMPLE_IMAGE = 'project/emailer/tests/resources/mountains.jpg'


@pytest.mark.django_db
def test_download_and_encode_thumbnails(
    monkeypatch, user_factory, date_dimension_factory, media_item_factory
):
    monkeypatch.setenv('MEDIA_UPLOAD_BUCKET_NAME', 'mock_bucket_name')
    monkeypatch.setenv('ENVIRONMENT', 'foobar')

    u = user_factory()

    d_a = date(1950, 9, 11)
    d_1 = date_dimension_factory(from_date=d_a)
    m_1 = media_item_factory(owner=u, create_day=d_1)

    d_b = date(1950, 9, 12)
    d_2 = date_dimension_factory(from_date=d_b)
    m_2 = media_item_factory(owner=u, create_day=d_2)

    media_items = [m.view() for m in [m_1, m_2]]

    def mock_copy_from_s3(bucket, key, destfile):
        assert key
        (owner_id, filename) = key.split('/')
        (image_id, ext) = filename.split('.')
        assert owner_id == str(u.id)
        assert image_id in [str(m.id) for m in [m_1, m_2]]

        image = '%s/%s' % (get_cwd(), SAMPLE_IMAGE)
        print(image)
        copyfile(image, destfile)
        assert exists(destfile)
        assert isfile(destfile)
        assert access(destfile, R_OK)

    monkeypatch.setattr(emailer.utils, 'get_image_from_s3', mock_copy_from_s3)

    download_and_encode_thumbnails(u.id, media_items, THUMBNAIL_DIMS)

    for mi in media_items:
        content_id = str(mi['content_id'])
        assert content_id in [str(m.id) for m in [m_1, m_2]]

        header_content_id = mi['encoded'].get('Content-ID')
        assert header_content_id == f'<{content_id}>'
        mime_image = mi['encoded']
        assert mime_image
        ext = mi['media_ext']
        assert ext
        assert_image_dims(mime_image, ext, THUMBNAIL_DIMS)


def assert_image_dims(mime_image, ext, dims):
    with NamedTemporaryFile(suffix=f'.{ext}') as tmp:
        payload = mime_image.get_payload(decode=True)
        tmp.write(payload)
        tmp.flush()
        im = Image.open(tmp.name)
        w, h = im.size
        assert dims[0] == w
        assert dims[1] == h


def get_cwd():
    d = getcwd()
    if d.endswith('/project'):
        return d.replace('/project', '')
    else:
        return d
