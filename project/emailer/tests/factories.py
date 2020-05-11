from datetime import date

import pytest

from date_dimension.tests.factories import DateDimensionFactory
from emailer.views.utils import DEFAULT_FROM_ADDRESS
from media_items.tests.factories import MediaItemFactory


@pytest.fixture
def media_items(custom_user, count_shared=5, count_shared_to=5):
    date_dimension = DateDimensionFactory(from_date=date(1950, 9, 11))
    media_items = MediaItemFactory.create_batch(
        size=count_shared, owner=custom_user, create_day=date_dimension
    )
    return media_items


class MockEmailerManager:
    mail_info = {}
    default_from_email_address = DEFAULT_FROM_ADDRESS
    send_count = 0
    mock_rendered_template = 'mock rendered template'

    @staticmethod
    def mock_thumbnailer(owner_id, media_items, dims):
        for media_item in media_items:
            media_item['encoded'] = 'mock_mime_image'

    @staticmethod
    def mock_renderer(tmpl, info):
        assert info == MockEmailerManager.mail_info
        return MockEmailerManager.mock_rendered_template

    class MockEmailer:
        def __init__(self, from_email, to, reply_to, subject, attachments, body):
            mem = MockEmailerManager
            assert mem.default_from_email_address == from_email
            to_addrs = [email for (email, email_id) in mem.mail_info['to'].items()]
            assert all(elem in to_addrs for elem in to)
            assert [mem.mail_info['from']] == reply_to
            assert mem.mail_info['subject'] == subject
            assert type(attachments) is list
            assert mem.mail_info['shared_count'] == len(attachments)
            assert body is not None
            assert body == mem.mock_rendered_template

        def attach_alternative(self, msg, msg_type):
            assert msg is not None
            assert msg == MockEmailerManager.mock_rendered_template
            assert msg_type is not None

        def send(self):
            MockEmailerManager.send_count = MockEmailerManager.send_count + 1
