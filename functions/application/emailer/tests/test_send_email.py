from datetime import date
from unittest.mock import patch
from uuid import uuid4

import pytest

from emailer.tests.factories import MockEmailerManager as mem
from emailer.views.send_email import EmailMultiAlternatives, send_email


@pytest.mark.django_db
def test_send_email(share_populated):
    share = share_populated
    mem.mail_info = share.view()

    # Why is this patching EmailMultiAlternatives in emailer.views?
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    with patch(
        'emailer.views.send_email.EmailMultiAlternatives', new=mem.MockEmailer
    ) as mock_mailer:
        send_email(
            mem.mail_info,
            'html_template.txt',
            'txt_template.txt',
            thumbnailer=mem.mock_thumbnailer,
            renderer=mem.mock_renderer,
        )
        assert mem.send_count == share.shared_count()
