import pytest


@pytest.mark.django_db
def test_media_item_create(media_item_factory):
    mi = media_item_factory()
    assert mi is not None
    assert mi.create_day is not None
    assert mi.create_date.year == mi.create_day.year
    assert mi.create_date.month == mi.create_day.month
    assert mi.create_date.day == mi.create_day.day
