from uuid import uuid4

import pytest


@pytest.mark.django_db
def test_media_item_view(authenticated_client, media_item_factory):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/%s/' % (u.id, mi.id)
    response = c.get(request_url)
    content = str(response.content)

    assert response.status_code == 200
    assert '<title>Media Item</title>' in content
    expected = '>%s<' % mi.create_day.this_date
    assert expected in content


@pytest.mark.django_db
def test_media_item_view_bad_request(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/%s/' % (uuid4(), mi.id)
    response = c.get(request_url)
    assert response.status_code == 400
