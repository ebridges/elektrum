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
    response = c.post('/media/request-upload/', {'mime_type': 'image/jpeg'})
    assert response.status_code == 201
    assert 'Location' in response
    assert urlparse(response['Location']) is not None

@pytest.mark.django_db
def test_sign_upload_request_logged_out(client):
    response = client.post('/media/request-upload/', {})
    assert response.status_code == 403


@pytest.mark.django_db
def test_sign_upload_request_mime_type_missing(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {})
    assert response.status_code == 400
    assert 'required parameter' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_mime_type_unsupported(authenticated_client):
    c, u = authenticated_client
    response = c.post('/media/request-upload/', {'mime_type': 'foobar'})
    assert response.status_code == 400
    assert 'not supported' in str(response.content)
