from logging import info
from django.core.mail import EmailMultiAlternatives
import os

from emailer.utils import download_and_encode_thumbnails, render_template

THUMBNAIL_DIMS = 222, 222
DEFAULT_FROM_ADDRESS = 'postmaster@%s' % os.environ['APPLICATION_DOMAIN_NAME']


def send_email(mail_info, body_text_tmpl, body_html_tmpl):
    info(f'send_email(%s, %s)' % (mail_info['shared_by'], mail_info['to']))

    download_and_encode_thumbnails(mail_info['owner_id'], mail_info['shared'], dims=THUMBNAIL_DIMS)
    attachments = [item['encoded'] for item in mail_info['shared']]
    info('thumbnails downloaded and encoded as attachments')

    text_message = render_template(body_text_tmpl, mail_info)

    msg = EmailMultiAlternatives(
        from_email=DEFAULT_FROM_ADDRESS,
        to=[mail_info['from']],
        reply_to=[mail_info['from']],
        bcc=mail_info['to'],
        subject=mail_info['subject'],
        attachments=attachments,
        body=text_message,
    )

    html_message = render_template(body_html_tmpl, mail_info)
    msg.attach_alternative(html_message, 'text/html')

    msg.send()
    info('Message sent.')
