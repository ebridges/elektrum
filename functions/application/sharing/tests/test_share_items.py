from datetime import date
from os.path import join
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.shortcuts import reverse
from django.template.loaders.locmem import Loader
from django.test import modify_settings
from django.core.exceptions import ObjectDoesNotExist

import pytest

from base.tests.util import MockGetRequest, MockPostRequest, assert_post_with_args
from base.views.errors import BadRequestException
from emailer.tests.factories import MockEmailerManager as mem
from sharing.models import Share, ShareState
from sharing.views.share_items import share_items, default_email_list, do_share_items


def mock_email_list(id):
    return ['aaa@example.com', 'bbb@example.com', 'ccc@example.com']


@pytest.mark.django_db
def test_share_items_missing_item(authenticated_client):
    c, u = authenticated_client
    assert_post_with_args(c, 'share-items', {'id': uuid4()}, 404)


@pytest.mark.django_db
def test_share_items_already_shared(share_populated):
    share = share_populated
    share.state = ShareState.SHARED
    share.save()

    user = share.shared_by
    request = MockPostRequest(user=user)
    response = share_items(request, share.id)
    assert response.status_code == 302
    assert response.url == reverse('share-log-item', kwargs={'id': share.id})


@pytest.mark.django_db
def test_share_items_new_form(share_populated):
    share = share_populated
    user = share.shared_by
    share.state = ShareState.INITIAL
    request = MockGetRequest(user=user, args={'id': share.id})

    response = share_items(request, share.id, email_list=mock_email_list)
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert f'{share.id}' in content
    assert f'{user.id}' in content
    assert f'{user.email}' in content


@pytest.mark.django_db
def test_share_items_share_action(share_populated):
    share = share_populated
    user = share.shared_by
    mem.mail_info = share.view()

    def validator(r):
        assert r == 'ok'

    def mock_share_items(user, share, data, emailer):
        assert user.id == user.id
        assert share.id == share.id
        assert data['from_address'] == user.email
        assert data['from_id'] == user.id
        with patch(
            'emailer.views.send_email.EmailMultiAlternatives', new=mem.MockEmailer
        ) as mock_mailer:
            emailer(
                mem.mail_info,
                'fake_template',
                'fake_template',
                thumbnailer=mem.mock_thumbnailer,
                renderer=mem.mock_renderer,
            )
        return 'ok'

    validate_share_items_action(share, 'share', validator, share_items_function=mock_share_items)


@pytest.mark.django_db
def test_share_items_draft_action(share_populated):
    share = share_populated

    def validator(r):
        user = share.shared_by
        s = Share.objects.get(pk=share.id)
        assert s.state == ShareState.DRAFT
        assert r.status_code == 302
        assert r.url == reverse('collections-view', kwargs={'owner_id': user.id})

    validate_share_items_action(share, 'draft', validator)


@pytest.mark.django_db
def test_share_items_cancel_action(share_populated):
    share = share_populated
    user = share.shared_by

    def validator(r):
        with pytest.raises(ObjectDoesNotExist):
            Share.objects.get(pk=share.id)
        assert r.status_code == 302
        assert r.url == reverse('share-log')

    validate_share_items_action(share, 'cancel', validator)


@pytest.mark.django_db
def test_share_items_invalid_action(share_populated):
    share = share_populated

    def validator(r):
        assert r.status_code == 400

    validate_share_items_action(share, 'foobar', validator)


def validate_share_items_action(s, action, validator, share_items_function=lambda *args: None):
    u = s.shared_by
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
    a_1 = audience_factory(email='ccc@example.com', shared_by=u)
    a_2 = audience_factory(email='bbb@example.com', shared_by=u)
    a_3 = audience_factory(email='aaa@example.com', shared_by=u)
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
def test_do_share_items(share_populated):
    share = share_populated
    user = share.shared_by

    data = {
        'from_id': user.id,
        'to_address': [a.email for a in share.shared_to.all()],
        'subject_line': 'fake subject',
        'share_message': 'fake message',
    }

    def mock_mailer(mail_info, text_tmpl, html_tmpl):
        assert mail_info['created'] is not None
        assert mail_info['modified'] is not None
        assert len(mail_info['to']) == 5
        assert mail_info['owner_id'] == user.id
        assert mail_info['shared_by'] == user.name()
        assert mail_info['from'] == user.email
        assert mail_info['subject'] == 'fake subject'
        assert mail_info['message'] == 'fake message'
        assert mail_info['shared_on'] is not None
        assert mail_info['state'] == ShareState.INITIAL
        assert len(mail_info['shared']) == 5
        assert mail_info['shared_count'] == share.shared_count()
        assert mail_info['to_count'] == share.to_count()

    response = do_share_items(user, share, data, emailer=mock_mailer)
    assert response.status_code == 302
    assert response.url == reverse('share-log-item', kwargs={'id': share.id})
    assert share.state == ShareState.SHARED
