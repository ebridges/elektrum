import os
import re
from urllib.parse import urlparse
from uuid import UUID
from datetime import datetime

import pytest

from users.tests.factories import USER_PASSWORD
from media_items.models import MediaItem


@pytest.mark.django_db
def test_sign_upload_request_success(authenticated_client):
    c, u = authenticated_client
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = 'abcdefgh'
    create_date = '2020-02-26T00:00:00'
    mime_type = 'image/jpeg'
    response = c.post('/media/request-upload/', {'create_date': '2020-02-26T00:00:00', 'mime_type': 'image/jpeg'})
    assert response.status_code == 201
    assert 'Location' in response
    assert urlparse(response['Location']) is not None
    assert 'X-Elektron-Media-Id' in response
    assert UUID(response['X-Elektron-Media-Id']) is not None

    expected = datetime.fromisoformat(create_date)
    pattern = expected.strftime('/%Y/%Y-%m-%d/%Y-%m-%dT%H%M%S_[a-z0-9]{8}.jpg')

    actual = MediaItem.objects.get(owner_id=u.id)
    assert actual.mime_type == mime_type
    assert re.match(pattern, actual.path)


@pytest.mark.django_db
def test_sign_upload_request_logged_out(client):
    response = client.post('/media/request-upload/', {})
    assert response.status_code == 403


@pytest.mark.django_db
def test_sign_upload_request_create_date_missing(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {})
    assert response.status_code == 400
    assert 'required parameter' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_create_date_empty(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'create_date': ''})
    assert response.status_code == 400
    assert 'must be in iso8601 format' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_create_date_invalid_format(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'create_date': 'Feb 26, 2020'})
    assert response.status_code == 400
    assert 'must be in iso8601 format' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_create_date_invalid_datetime(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'create_date': '2020-01-42T25:00:00'})
    assert response.status_code == 400
    assert 'must be a valid datetime' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_mime_type_missing(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'create_date': '2020-02-26T00:00:00'})
    assert response.status_code == 400
    assert 'required parameter' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_mime_type_unsupported(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'create_date': '2020-02-26T00:00:00', 'mime_type': 'foobar'})
    assert response.status_code == 400
    assert 'not supported' in str(response.content)
