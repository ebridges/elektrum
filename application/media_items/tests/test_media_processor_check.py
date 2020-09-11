from uuid import uuid4
from unittest.mock import MagicMock
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

from pytest import raises, mark

from base.views.errors import MethodNotAllowedException, ForbiddenException
from media_items.views.media_processor_check import validate, check_exists
from users.models import CustomUser


@mark.django_db
def test_check_exists_normal_case(media_item_factory):
    mi = media_item_factory()
    response = check_exists(mi.id)
    assert response.status_code == 200


@mark.django_db
def test_check_exists_normal_case():
    response = check_exists(uuid4())
    assert response.status_code == 404


@mark.django_db
def test_validate_request_normal_case(user_factory):
    expected_id = uuid4()
    u = user_factory()
    under_test = setup_validate_request_mock(u)
    assert validate(under_test, u.id) is None


@mark.django_db
def test_validate_request_invalid_method(user_factory):
    u = user_factory()
    under_test = setup_validate_request_mock(u, method='POST')
    with raises(MethodNotAllowedException):
        validate(under_test, u.id)


def test_validate_request_forbidden():
    u = AnonymousUser()
    under_test = setup_validate_request_mock(u)
    with raises(ForbiddenException):
        validate(under_test, u.id)

    under_test = setup_validate_request_mock(u)
    with raises(ForbiddenException):
        validate(under_test, uuid4())


def setup_validate_request_mock(user, method='HEAD'):
    mock_request = HttpRequest()
    mock_request.user = user
    mock_request.method = method
    return mock_request
