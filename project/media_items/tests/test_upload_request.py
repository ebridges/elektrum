import re
from urllib.parse import urlparse
from uuid import UUID
from datetime import datetime

import pytest

from django.shortcuts import reverse

from users.tests.factories import USER_PASSWORD
from media_items.models import MediaItem


@pytest.mark.django_db
def test_sign_upload_request_success(authenticated_client, monkeypatch):
    c, u = authenticated_client
    monkeypatch.setenv('MEDIA_UPLOAD_BUCKET_NAME', 'abcdefgh')
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'XXXX22XXXXXX4XX2XXXX')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', '0AbbbCtSAfgpoi71w8WERw8AviFYatdIV3xcPGry')
    mime_type = 'image/jpeg'
    request_url = reverse('upload-request')
    response = c.post(request_url, {'mime_type': mime_type})
    assert response.status_code == 201
    assert 'Location' in response
    assert urlparse(response['Location']) is not None


@pytest.mark.django_db
def test_sign_upload_request_logged_out(client):
    url = reverse('upload-request')
    response = client.post(url, {})
    assert response.status_code == 403


@pytest.mark.django_db
def test_sign_upload_request_mime_type_missing(authenticated_client):
    c, u = authenticated_client
    url = reverse('upload-request')
    response = c.post(url, {})
    assert response.status_code == 400
    assert 'required parameter' in str(response.content)


@pytest.mark.django_db
def test_sign_upload_request_mime_type_unsupported(authenticated_client):
    c, u = authenticated_client
    url = reverse('upload-request')
    response = c.post(url, {'mime_type': 'foobar'})
    assert response.status_code == 400
    assert 'not supported' in str(response.content)
