from uuid import uuid4
import pytest


@pytest.mark.django_db
def test_media_item_collections_view(media_item_factory, authenticated_client):
    c, u = authenticated_client
    mi = media_item_factory(owner=u)
    request_url = '/media/%s/' % u.id
    response = c.get(request_url)
    content = str(response.content)
    assert response.status_code == 200
    assert 'Collections available for %s' % u.username in content
    assert '<td>%s</td>' % mi.create_day.year in content


@pytest.mark.django_db
def test_media_item_collections_view_bad_request(media_item_factory, authenticated_client):
    c, u = authenticated_client
    media_item_factory(owner=u)
    request_url = '/media/%s/' % uuid4()
    response = c.get(request_url)
    assert response.status_code == 400

