from datetime import date
from os.path import join
from uuid import uuid4

from django.conf import settings
from django.shortcuts import reverse
from django.template.loaders.locmem import Loader
from django.test import modify_settings
from django.core.exceptions import ObjectDoesNotExist

import pytest

from base.views.errors import BadRequestException
from sharing.models import Share, ShareState
from sharing.views.share_items import share_items, default_email_list, do_share_items


def mock_email_list(id):
    return ['aaa@example.com', 'bbb@example.com', 'ccc@example.com']


class MockPostRequest:
    def __init__(self, user, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'POST'
        self.POST = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


class MockGetRequest:
    def __init__(self, user, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'GET'
        self.GET = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


def assert_post_with_args(client, url_name, args, expected_code):
    request_url = reverse(url_name, kwargs=args)
    response = client.post(request_url)
    assert response.status_code == expected_code
    return response


@pytest.mark.django_db
def test_share_items_missing_item(authenticated_client):
    c, u = authenticated_client
    assert_post_with_args(c, 'share-items', {'id': uuid4()}, 404)


@pytest.mark.django_db
def test_share_items_already_shared(user_factory, share_factory):
    u = user_factory()
    request = MockPostRequest(user=u)
    share = share_factory(state=ShareState.SHARED, shared_by=u)
    response = share_items(request, share.id)
    assert response.status_code == 302
    assert response.url == f'/sharing/share-log/{share.id}/'


@pytest.mark.django_db
def test_share_items_new_form(user_factory, share_factory):
    u = user_factory()
    share = share_factory(shared_by=u)
    share.state = ShareState.INITIAL
    request = MockGetRequest(user=u, args={'id': share.id})

    response = share_items(request, share.id, email_list=mock_email_list)
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert f'{share.id}' in content
    assert f'{u.id}' in content
    assert f'{u.email}' in content


@pytest.mark.django_db
def test_share_items_share_action(user_factory, share_factory):
    u = user_factory()
    s = share_factory(shared_by=u)

    def validator(r):
        assert r == 'ok'

    def mock_share_items(user, share, data, emailer=lambda *args: None):
        assert user.id == u.id
        assert share.id == s.id
        assert data['from_address'] == u.email
        assert data['from_id'] == u.id
        return 'ok'

    validate_share_items_action(u, s, 'share', validator, share_items_function=mock_share_items)


@pytest.mark.django_db
def test_share_items_draft_action(user_factory, share_factory):
    u = user_factory()
    s = share_factory(shared_by=u)

    def validator(r):
        share = Share.objects.get(pk=s.id)
        assert share.state == ShareState.DRAFT
        assert r.status_code == 302
        assert r.url == reverse('collections-view', kwargs={'owner_id': u.id})

    validate_share_items_action(u, s, 'draft', validator)


@pytest.mark.django_db
def test_share_items_cancel_action(user_factory, share_factory):
    u = user_factory()
    s = share_factory(shared_by=u)

    def validator(r):
        with pytest.raises(ObjectDoesNotExist):
            share = Share.objects.get(pk=s.id)
        assert r.status_code == 302
        assert r.url == reverse('share-log')

    validate_share_items_action(u, s, 'cancel', validator)


@pytest.mark.django_db
def test_share_items_invalid_action(user_factory, share_factory):
    u = user_factory()
    s = share_factory(shared_by=u)

    def validator(r):
        assert r.status_code == 400

    validate_share_items_action(u, s, 'foobar', validator)


def validate_share_items_action(u, s, action, validator, share_items_function=lambda *args: None):
    s.state = ShareState.INITIAL
    post_data = {
        'id': s.id,
        'from_id': u.id,
        'action': action,
        'to_address': 'abc@example.com',
        'subject_line': 'fake subject',
        'share_message': 'fake message',
    }
    request = MockPostRequest(user=u, args=post_data)
    response = share_items(
        request, s.id, email_list=mock_email_list, share_items=share_items_function
    )
    validator(response)


@pytest.mark.django_db
def test_default_email_list(user_factory, audience_factory):
    u = user_factory()
    a_1 = audience_factory(email='aaa@example.com', shared_by=u)
    a_2 = audience_factory(email='bbb@example.com', shared_by=u)
    a_3 = audience_factory(email='ccc@example.com', shared_by=u)
    a_4 = audience_factory(email='ddd@example.com', shared_by=u, unsubscribed=True)

    emails = default_email_list(u.id)

    assert len(emails) == 3  # unsubscribed email filtered out
    assert emails[0] == 'aaa@example.com'
    assert emails[1] == 'bbb@example.com'
    assert emails[2] == 'ccc@example.com'


@pytest.mark.django_db
def test_do_share_items_missing_shared_items(user_factory, share_factory):
    u = user_factory()
    s = share_factory(shared_by=u)

    data = {'from_id': u.id}
    with pytest.raises(BadRequestException):
        data['to_address'] = ['aaa@example.com', 'bbb@example.com']
        data['shared'] = []
        do_share_items(u, s, data)

    with pytest.raises(BadRequestException):
        data['to_address'] = []
        data['shared'] = ['foobar', 'asdfasdf']
        do_share_items(u, s, data)

    with pytest.raises(BadRequestException):
        data['to_address'] = []
        data['shared'] = []
        do_share_items(u, s, data)


@pytest.mark.django_db
def test_do_share_items(
    user_factory, audience_factory, share_factory, media_item_factory, date_dimension_factory
):
    u = user_factory()

    d_a = date(1950, 9, 11)
    d_1 = date_dimension_factory(from_date=d_a)
    m_1 = media_item_factory(owner=u, create_day=d_1)

    d_b = date(1950, 9, 12)
    d_2 = date_dimension_factory(from_date=d_b)
    m_2 = media_item_factory(owner=u, create_day=d_2)

    a_1 = audience_factory(email='aaa@example.com', shared_by=u)
    a_2 = audience_factory(email='bbb@example.com', shared_by=u)

    s = share_factory(shared_by=u, shared_to=[a_1, a_2], shared=[m_1, m_2])

    data = {
        'from_id': u.id,
        'to_address': [a_1.email, a_2.email],
        'subject_line': 'fake subject',
        'share_message': 'fake message',
    }

    def mock_mailer(mail_info, text_tmpl, html_tmpl):
        assert mail_info['created'] is not None
        assert mail_info['modified'] is not None
        assert len(mail_info['to']) == 2
        assert mail_info['owner_id'] == u.id
        assert mail_info['shared_by'] == u.name()
        assert mail_info['from'] == u.email
        assert mail_info['subject'] == 'fake subject'
        assert mail_info['message'] == 'fake message'
        assert mail_info['shared_on'] is not None
        assert mail_info['state'] == ShareState.INITIAL
        assert len(mail_info['shared']) == 2
        assert mail_info['shared_count'] == 2
        assert mail_info['to_count'] == 2

    response = do_share_items(u, s, data, emailer=mock_mailer)
    assert response.status_code == 302
    assert response.url == reverse('share-log-item', kwargs={'id': s.id})
    assert s.state == ShareState.SHARED
