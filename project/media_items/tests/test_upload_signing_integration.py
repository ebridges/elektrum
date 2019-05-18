import re
from urllib.parse import urlparse
from uuid import UUID
from datetime import datetime

import pytest

from users.tests.factories import USER_PASSWORD
from media_items.models import MediaItem


@pytest.mark.django_db
def test_sign_upload_request_success(authenticated_client, monkeypatch):
    c, u = authenticated_client
    monkeypatch.setenv('AWS_UPLOAD_BUCKET_NAME', 'abcdefgh')
    mime_type = 'image/jpeg'
    request_url = '/media/%s/request-upload/' % u.id
    response = c.post(request_url, {'mime_type': mime_type})
    assert response.status_code == 201
    assert 'Location' in response
    assert urlparse(response['Location']) is not None


@pytest.mark.django_db
def test_sign_upload_request_logged_out(client):
    response = client.post('/media/e50cd266-7376-11e9-b0b2-320017981ea0/request-upload/', {})
    assert response.status_code == 403


@pytest.mark.django_db
def test_sign_upload_request_mime_type_missing(authenticated_client):
    c, u = authenticated_client
    request_url = '/media/%s/request-upload/' % u.id
    response = c.post(request_url, {})
    assert response.status_code == 400
    assert 'required parameter' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_mime_type_unsupported(authenticated_client):
    c, u = authenticated_client
    request_url = '/media/%s/request-upload/' % u.id
    response = c.post(request_url, {'mime_type': 'foobar'})
    assert response.status_code == 400
    assert 'not supported' in str(response.content)
