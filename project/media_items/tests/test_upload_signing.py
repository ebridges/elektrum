import os
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import pytest

from media_items.upload_signing import *
from base.tests.util import match_image_key

@pytest.mark.django_db
def test_create_signed_upload_url(user_factory):
    bucket_name = 'opqrstu'
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = bucket_name
    type = 'image/jpeg'
    user = user_factory()
    actual_url = create_signed_upload_url(user, type)
    qs = parse_qs(actual_url.query)
    assert actual_url.scheme == 'https'
    assert actual_url.hostname == '%s.s3.amazonaws.com' % bucket_name
    assert 'X-Amz-Credential' in qs
    assert 'X-Amz-Signature' in qs
    assert 'X-Amz-Expires' in qs

    m = match_image_key(user.id, actual_url.path)
    assert m is not None
    assert m.group('user_id') == str(user.id)
    assert m.group('image_id') is not None
    assert m.group('extension') == supported_upload_types[type]


@pytest.mark.django_db
def test_create_signed_url(user_factory):
    bucket_name = 'opqrstu'
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = bucket_name
    user = user_factory()
    expected_credentials = lookup_user_upload_credentials(user)
    upload_key = 'abcdefg'
    url = create_signed_url(expected_credentials, upload_key)
    qs = parse_qs(url.query)
    actual_credential = qs['X-Amz-Credential'][0].split('/')[0]
    assert url.scheme == 'https'
    assert url.hostname == '%s.s3.amazonaws.com' % bucket_name
    assert url.path == '/%s' % upload_key
    assert actual_credential == expected_credentials[0]


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


def test_extension_from_type_failure():
    with pytest.raises(KeyError):
        extension_from_type('foobar')


def test_extension_from_type():
    type = extension_from_type('image/jpeg')
    assert type == 'jpg'
