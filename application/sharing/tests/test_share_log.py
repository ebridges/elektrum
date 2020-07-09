from datetime import date
import pytest

from django.shortcuts import reverse


@pytest.mark.django_db
def test_share_log(
    authenticated_client,
    share_factory,
    audience_factory,
    date_dimension_factory,
    media_item_factory,
):
    a, u = authenticated_client
    batch_size = 10
    dd = date_dimension_factory(from_date=date(1966, 2, 26))
    mi_list = media_item_factory.create_batch(size=batch_size, owner=u, create_day=dd)
    to = audience_factory.create_batch(size=batch_size, shared_by=u)
    shares = share_factory.create_batch(size=batch_size, shared_by=u, shared_to=to, shared=mi_list)

    url = reverse('share-log')

    response = a.get(url)
    content = str(response.content)

    assert response.status_code == 200
    for share in shares:
        assert str(share.id) in content
