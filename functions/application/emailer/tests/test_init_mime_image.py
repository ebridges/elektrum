import pytest

from emailer.views.utils import init_mime_image


@pytest.mark.django_db
def test_init_mime_image(media_items):
    JPEG_HEADER = b'\xff\xd8\xff\xe1-\xfcExif\x00\x00MM\x00*\x00\x00\x00\x08'
    for media_item in media_items:
        view = media_item.view()
        init_mime_image(JPEG_HEADER, view)
        assert view['encoded'] is not None
        image = view['encoded']
        assert image.get_content_type() == 'image/jpeg'
        assert image.get('Content-ID') is not None
        assert image.get('Content-ID') == '<%s>' % view['item_id']
        assert image.get('Content-Location') is not None
        assert image.get('Content-Location') == view['media_item_url']
        view['content_id'] == view['item_id']
