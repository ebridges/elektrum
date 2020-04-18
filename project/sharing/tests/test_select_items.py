from datetime import date
from uuid import uuid4

from django.shortcuts import reverse

import pytest

from sharing.models import Share, ShareState


@pytest.mark.django_db
def test_select_items_method_unsupported(authenticated_client):
    c, u = authenticated_client
    request_url = reverse('select-items')
    response = c.get(request_url)
    assert response.status_code == 405


@pytest.mark.django_db
def test_select_items_bad_request(authenticated_client):
    c, u = authenticated_client
    request_url = reverse('select-items')
    response = c.post(request_url, {'items-to-share': []})
    assert response.status_code == 400


@pytest.mark.django_db
def test_select_items_new_share(authenticated_client, media_item_factory):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = reverse('select-items')
    response = c.post(request_url, {'items-to-share': [str(mi.id)]})
    print('Status code %s' % response.status_code)
    print('Response content: %s' % response.content)
    assert response.status_code == 302

    share = Share.objects.filter(shared_by=u).first()
    assert share.state == ShareState.INITIAL
    assert share.shared_by == u
    shared_media = share.shared.filter(id=mi.id)
    assert len(shared_media) == 1


@pytest.mark.django_db
def test_select_items_existing_share(
    authenticated_client, media_item_factory, share_factory, date_dimension_factory
):
    c, u = authenticated_client

    d_a = date(1950, 9, 11)
    d_1 = date_dimension_factory(from_date=d_a)
    mi_1 = media_item_factory(owner=u, create_day=d_1)

    d_b = date(1950, 9, 12)
    d_2 = date_dimension_factory(from_date=d_b)
    mi_2 = media_item_factory(owner=u, create_day=d_2)

    s = share_factory(shared_by=u)
    assert s.shared_by == u

    request_url = reverse('select-items')
    request_data = {'share-id': str(s.id), 'items-to-share': [str(mi.id) for mi in (mi_1, mi_2)]}
    response = c.post(request_url, request_data)

    assert response.status_code == 302

    share = Share.objects.filter(shared_by=u).first()
    assert share.state == ShareState.INITIAL
    assert share.shared_by == u
    shared_media = share.shared.all()
    assert len(shared_media) == 2
