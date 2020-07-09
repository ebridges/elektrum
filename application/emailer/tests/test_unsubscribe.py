from uuid import uuid4

import pytest

from django.shortcuts import reverse

from base.tests.util import MockGetRequest, MockPostRequest
from emailer.views.unsubscribe import unsubscribe


@pytest.mark.django_db
def test_unsubscribe_missing_item(user_factory, audience_factory):
    request = MockGetRequest()
    response = unsubscribe(request, uuid4())
    assert response.status_code == 404


@pytest.mark.django_db
def test_unsubscribe_get(audience_factory):
    a = audience_factory()
    request = MockGetRequest()
    response = unsubscribe(request, a.id)
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert a.email in content
    assert a.shared_by.name() in content
    assert str(a.id) in content


@pytest.mark.django_db
def test_unsubscribe_post(audience_factory):
    a = audience_factory()
    request = MockPostRequest()
    response = unsubscribe(request, a.id)
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert a.email in content
    assert a.shared_by.name() in content
    assert 'has been unsubscribed' in content
