import pytest

from django.shortcuts import reverse

from sharing.views.share_log_delete import share_log_delete


class MockGetRequest:
    def __init__(self, user, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'GET'
        self.GET = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


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
