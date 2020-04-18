import pytest

from django.http import HttpResponseBadRequest

from base.tests.util import MockGetRequest
from sharing.views.share_log_item import share_log_item


@pytest.mark.django_db
def test_share_log_item_missing_item(share_factory):
    s = share_factory()
    request = MockGetRequest(user=s.shared_by)
    response = share_log_item(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_share_log_item(share_factory):
    s = share_factory()
    request = MockGetRequest(user=s.shared_by)

    response = share_log_item(request, id=s.id)
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert str(s.id) in content
