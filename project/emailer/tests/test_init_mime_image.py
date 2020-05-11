import pytest

from emailer.views.utils import init_mime_image


@pytest.mark.django_db
def test_init_mime_image(media_items):
    for media_item in media_items:
        init_mime_image(b'', media_item)
        assert media_item['encoded'] is not None
        image = media_item['encoded']
        assert image.get('Content-ID') is not None
        assert image.get('Content-ID') == '<%s>' % media_item['item_id']
        assert image.get('Content-Location') is not None
        assert image.get('Content-Location') == media_item['media_item_url']
        media_item['content_id'] == media_item['item_id']
