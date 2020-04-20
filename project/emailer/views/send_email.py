from logging import info
from os import environ

from django.core.mail import EmailMultiAlternatives

from emailer.views.utils import (
    download_and_encode_thumbnails,
    render_template,
    THUMBNAIL_DIMS,
    DEFAULT_FROM_ADDRESS,
)


def send_email(
    mail_info,
    body_text_tmpl,
    body_html_tmpl,
    thumbnailer=download_and_encode_thumbnails,
    renderer=render_template,
):
    info(f'send_email(%s, %s)' % (mail_info['shared_by'], mail_info['to']))

    thumbnailer(mail_info['owner_id'], mail_info['shared'], dims=THUMBNAIL_DIMS)
    attachments = [item['encoded'] for item in mail_info['shared']]
    info('thumbnails downloaded and encoded as attachments')

    cnt = 0
    addrs = mail_info['to']
    for (email, email_id) in addrs.items():
        mail_info['email_id'] = email_id
        text_message = renderer(body_text_tmpl, mail_info)

        msg = EmailMultiAlternatives(
            from_email=DEFAULT_FROM_ADDRESS,
            to=[email],
            reply_to=[mail_info['from']],
            subject=mail_info['subject'],
            attachments=attachments,
            body=text_message,
        )

        html_message = renderer(body_html_tmpl, mail_info)
        msg.attach_alternative(html_message, 'text/html')

        msg.send()
        cnt = cnt + 1

        info(f'Message sent to {email}')
    info(f'{cnt} emails sent')
