from uuid import uuid4

import pytest


@pytest.mark.django_db
def test_collections_view(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/' % u.id
    response = c.get(request_url)
    content = str(response.content)
    assert response.status_code == 200
    assert '<title>Collections Home</title>' in content
    expected = '&nbsp;%s' % mi.create_day.year
    assert expected in content


@pytest.mark.django_db
def test_collections_view_bad_request(media_item_factory, authenticated_client):
    c, u = authenticated_client
    media_item_factory(owner=u)
    request_url = '/media/%s/' % uuid4()
    response = c.get(request_url)
    assert response.status_code == 400
