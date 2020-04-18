from datetime import date
from uuid import uuid4

import pytest


@pytest.mark.django_db
def test_media_item_list_view(authenticated_client, media_item_factory, date_dimension_factory):
    c, u = authenticated_client
    batch_size = 10
    dd = date_dimension_factory(from_date=date(1966, 2, 26))
    mi_list = media_item_factory.create_batch(size=batch_size, owner=u, create_day=dd)
    assert len(mi_list) == batch_size
    mi = mi_list[0]
    request_url = '/media/%s/%s/%s/' % (u.id, mi.create_day.year, mi.create_day.iso_date)
    response = c.get(request_url)
    content = str(response.content)

    assert response.status_code == 200
    for item in mi_list:
        assert '/%s' % str(item.id) in content


@pytest.mark.django_db
def test_media_item_list_view_bad_request(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/%s/%s/' % (uuid4(), mi.create_day.year, mi.create_day.iso_date)
    response = c.get(request_url)
    assert response.status_code == 400
