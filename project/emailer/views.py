from logging import info
from django.core.mail import EmailMultiAlternatives
import os

from emailer.utils import download_and_encode_thumbnails, render_template

THUMBNAIL_DIMS = 222, 222
DEFAULT_FROM_ADDRESS = 'postmaster@%s' % os.environ['APPLICATION_DOMAIN_NAME']


def send_email(sender, to, subject, body_text_tmpl=None, body_html_tmpl=None, context={}):
    info(f'send_email({sender}, {to})')

    download_and_encode_thumbnails(context['owner_id'], context['objects'], dims=THUMBNAIL_DIMS)
    attachments = [item['encoded'] for item in context['objects']]
    info('thumbnails downloaded and encoded as attachments')

    text_message = render_template(body_text_tmpl, context)

    msg = EmailMultiAlternatives(
        from_email=DEFAULT_FROM_ADDRESS,
        to=[sender],
        reply_to=[sender],
        bcc=to,
        subject=subject,
        attachments=attachments,
        body=text_message,
    )

    html_message = render_template(body_html_tmpl, context)
    msg.attach_alternative(html_message, 'text/html')

    msg.send()
    info('Message sent.')
