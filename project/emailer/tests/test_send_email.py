from datetime import date
from unittest.mock import patch
from uuid import uuid4

from emailer.views.send_email import EmailMultiAlternatives
import pytest

from emailer.views.send_email import send_email, EmailMultiAlternatives
from emailer.views.utils import DEFAULT_FROM_ADDRESS


@pytest.mark.django_db
def test_send_email(
    user_factory, date_dimension_factory, media_item_factory, audience_factory, share_factory
):
    u = user_factory()

    media_items = []
    d_a = date(1950, 9, 11)
    d_1 = date_dimension_factory(from_date=d_a)
    media_items.append(media_item_factory(owner=u, create_day=d_1))

    d_b = date(1950, 9, 12)
    d_2 = date_dimension_factory(from_date=d_b)
    media_items.append(media_item_factory(owner=u, create_day=d_2))

    audiences = []
    audiences.append(audience_factory(email='aaa@example.com', shared_by=u))
    audiences.append(audience_factory(email='bbb@example.com', shared_by=u))

    s = share_factory(shared_by=u, shared_to=audiences, shared=media_items)

    mail_info = s.view()

    t = 'mock rendered template'

    def mock_thumbnailer(owner_id, media_items, dims):
        for media_item in media_items:
            media_item['encoded'] = 'mock_mime_image'

    def mock_render_template(tmpl, info):
        assert info == mail_info
        return t

    class MockEmailer:
        def __init__(self, from_email, to, reply_to, subject, attachments, body):
            assert DEFAULT_FROM_ADDRESS == from_email
            to_addrs = [email for (email, email_id) in mail_info['to'].items()]
            assert all(elem in to_addrs for elem in to)
            assert [mail_info['from']] == reply_to
            assert mail_info['subject'] == subject
            assert type(attachments) is list
            assert len(media_items) == len(attachments)
            assert t == body

        def attach_alternative(self, msg, msg_type):
            assert t == msg
            assert msg_type is not None

        def send(self):
            pass

    # Why is this patching EmailMultiAlternatives in emailer.views?
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    with patch('emailer.views.send_email.EmailMultiAlternatives', new=MockEmailer) as mock_mailer:
        sent_count = send_email(
            mail_info,
            'html_template.txt',
            'txt_template.txt',
            thumbnailer=mock_thumbnailer,
            renderer=mock_render_template,
        )
        assert sent_count == len(audiences)
