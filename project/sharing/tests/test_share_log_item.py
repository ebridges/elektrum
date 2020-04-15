import pytest

from django.http import HttpResponseBadRequest

from sharing.views.share_log_item import share_log_item


class MockGetRequest:
    def __init__(self, user, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'GET'
        self.GET = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


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
