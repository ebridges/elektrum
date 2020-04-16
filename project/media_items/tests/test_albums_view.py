from uuid import uuid4

import pytest


@pytest.mark.django_db
def test_albums_view(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/%s/' % (u.id, mi.create_day.year)
    response = c.get(request_url)
    content = str(response.content)
    assert response.status_code == 200
    assert '<title>Album Home</title>' in content
    expected = '>%s<' % mi.create_day.year
    assert expected in content


@pytest.mark.django_db
def test_albums_view_bad_request(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/%s/' % (uuid4(), mi.create_day.year)
    response = c.get(request_url)
    assert response.status_code == 400
