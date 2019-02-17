import os
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import pytest

from media_items.upload_signing import *


@pytest.mark.django_db
def test_record_upload_request(user_factory):
    user = user_factory()
    upload_url = 'https://[BUCKET].s3.amazonaws.com/[USER_ID]/2020/2020-02-26/2020-02-26T112343_[' \
                 'SLUG].jpg?AWSAccessKeyId=[KEY]&Signature=[SIG]&Expires=1550426152'
    upload_size = 12345
    mime_type = 'image/jpeg'
    item_id = record_upload_request(user, upload_url, upload_size, mime_type)
    item = MediaItem.objects.get(id=item_id)

    user_id, path = split_upload_path(urlparse(upload_url).path)
    assert item.owner.id == user.id
    assert item.owner.id == user_id
    assert item.file_size == upload_size
    assert item.media_type == mime_type
    assert item.path == path


@pytest.mark.django_db
def test_create_signed_upload_url(user_factory):
    bucket_name = 'opqrstu'
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = bucket_name
    create_iso = '2020-02-26T11:23:43'
    create_date = datetime.fromisoformat(create_iso)
    type = 'image/jpeg'
    user = user_factory()
    actual_url = create_signed_upload_url(user, create_date, type)
    o = urlparse(actual_url)
    qs = parse_qs(o.query)
    assert o.scheme == 'https'
    assert o.hostname == '%s.s3.amazonaws.com' % bucket_name
    assert 'AWSAccessKeyId' in qs
    assert 'Signature' in qs
    assert 'Expires' in qs

    expected_key = r'/%s/([0-9]{4})/([0-9]{4}-[0-9]{2}-[0-9]{2})/([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})_[0-9a-z]{8}\.(' \
                   r'[a-z]{3})' % user.id

    m = re.match(expected_key, o.path)
    assert m is not None
    assert m.group(1) == str(create_date.year)
    assert m.group(2) == f'{create_date.year:04}-{create_date.month:02}-{create_date.day:02}'
    assert m.group(3) == create_date.strftime('%Y-%m-%d''T''%H%M%S')
    assert m.group(4) == supported_upload_types[type]


@pytest.mark.django_db
def test_create_signed_url(user_factory):
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = 'opqrstu'
    user = user_factory()
    credentials = lookup_user_upload_credentials(user)
    upload_key = 'abcdefg'
    url = create_signed_url(credentials, upload_key)
    o = urlparse(url)
    qs = parse_qs(o.query)
    assert o.scheme == 'https'
    assert o.hostname == '%s.s3.amazonaws.com' % credentials[2]
    assert o.path == '/%s' % upload_key
    assert qs['AWSAccessKeyId'][0] == credentials[0]


@pytest.mark.django_db
def test_create_upload_key_with_slug(user_factory):
    user = user_factory()
    dt = datetime(year=2018, month=7, day=12, hour=7, minute=9, second=33)
    slug = 'abcdefgh'
    mtype = 'image/jpeg'
    key = create_upload_key(user, dt, mtype, slug)
    assert key == '%s/%s/%s/%s_%s.%s' % (user.id, '2018', '2018-07-12', '2018-07-12T070933', slug,
                                         supported_upload_types[mtype])


@pytest.mark.django_db
def test_create_upload_key(user_factory):
    user = user_factory()
    dt = datetime(year=2018, month=7, day=12, hour=7, minute=9, second=33)
    mtype = 'image/jpeg'
    actual_key = create_upload_key(user, dt, mtype)
    expected_key = '%s/%s/%s/%s_[a-z0-9]{8}.%s' % (user.id, '2018', '2018-07-12', '2018-07-12T070933',
                                                   supported_upload_types[mtype])
    assert re.match(expected_key, actual_key)


@pytest.mark.django_db
def test_lookup_user_upload_credentials(user_factory):
    os.environ['AWS_ACCESS_KEY_ID'] = 'abcdefg'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'hijklmn'
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = 'opqrstu'
    user = user_factory()
    credentials = lookup_user_upload_credentials(user)
    assert credentials[0] == 'abcdefg'
    assert credentials[1] == 'hijklmn'
    assert credentials[2] == 'opqrstu'


def test_generate_slug():
    slug_3 = generate_slug(3)
    assert len(slug_3) == 3

    slug_8 = generate_slug()
    assert len(slug_8) == 8


def test_extension_from_type():
    with pytest.raises(KeyError):
        extension_from_type('foobar')

    type = extension_from_type('image/jpeg')
    assert type == 'jpg'


def test_split_upload_path():
    u = '/[USER_ID]/2020/2020-02-26/2020-02-26T112343_[SLUG].jpg'
    a, b = split_upload_path(u)
    assert a == '[USER_ID]'
    assert b == '/2020/2020-02-26/2020-02-26T112343_[SLUG].jpg'
