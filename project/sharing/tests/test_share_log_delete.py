import pytest

from django.shortcuts import reverse

from base.tests.util import MockGetRequest
from sharing.views.share_log_delete import share_log_delete


@pytest.mark.django_db
def test_share_log_delete_missing_item(share_factory):
    s = share_factory()
    request = MockGetRequest(user=s.shared_by)
    response = share_log_delete(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_share_log_delete(share_factory):
    s = share_factory()
    request = MockGetRequest(user=s.shared_by)
    response = share_log_delete(request, id=s.id)
    assert response.status_code == 302
    assert response.url == reverse('share-log')
