import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import pytest

from media_items.views.upload_util import (
    create_signed_upload_url,
    supported_upload_types,
    create_upload_key,
    create_signed_url,
    extension_from_type,
)
from base.tests.util import match_image_key


@pytest.mark.django_db
def test_create_signed_upload_url(user_factory, monkeypatch):
    bucket_name = 'opqrstu'
    monkeypatch.setenv('MEDIA_UPLOAD_BUCKET_NAME', bucket_name)
    mime_type = 'image/jpeg'
    user = user_factory()
    actual_url = create_signed_upload_url(user, mime_type)
    au = urlparse(actual_url)
    qs = parse_qs(au.query)
    assert au.scheme == 'https'
    assert au.hostname == '%s.s3.amazonaws.com' % bucket_name
    assert 'X-Amz-Credential' in qs
    assert 'X-Amz-Signature' in qs
    assert 'X-Amz-Expires' in qs

    m = match_image_key(user.id, au.path)
    assert m is not None
    assert m.group('user_id') == str(user.id)
    assert m.group('image_id') is not None
    assert m.group('extension') == supported_upload_types[mime_type]


@pytest.mark.django_db
def test_create_signed_url(user_factory, monkeypatch):
    bucket_name = 'opqrstu'
    user = user_factory()
    upload_key = 'abcdefg'
    mim_type = 'text/plain'
    url = create_signed_url(bucket_name, upload_key, mim_type)
    qs = parse_qs(url.query)
    assert url.scheme == 'https'
    assert url.hostname == '%s.s3.amazonaws.com' % bucket_name
    assert url.path == '/%s' % upload_key


@pytest.mark.django_db
def test_create_upload_key(user_factory):
    user = user_factory()
    mtype = 'image/jpeg'
    key = create_upload_key(user, mtype)
    m = match_image_key(user.id, key)
    assert m is not None
    assert m.group('user_id') == str(user.id)
    assert m.group('image_id') is not None
    assert m.group('extension') == supported_upload_types[mtype]


def test_extension_from_type_failure():
    with pytest.raises(KeyError):
        extension_from_type('foobar')


def test_extension_from_type():
    extension = extension_from_type('image/jpeg')
    assert extension == 'jpg'
