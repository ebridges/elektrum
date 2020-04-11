from logging import info
from os import environ

from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render

from emailer.utils import download_and_encode_thumbnails, render_template
from sharing.models import Audience

THUMBNAIL_DIMS = 222, 222
DEFAULT_FROM_ADDRESS = 'postmaster@%s' % environ['APPLICATION_DOMAIN_NAME']


def unsubscribe(request, email_id):
    email = Audience.objects.get(pk=email_id)
    owner = email.shared_by
    context = {'shared_to': email.email, 'shared_by': owner.name(), 'email_id': email.id}

    if request.method == 'POST':
        email.unsubscribed = True
        email.save()
        context['unsubscribed'] = True

    return render(request, 'emailer/unsubscribe.html', context)


def send_email(mail_info, body_text_tmpl, body_html_tmpl):
    info(f'send_email(%s, %s)' % (mail_info['shared_by'], mail_info['to']))

    download_and_encode_thumbnails(mail_info['owner_id'], mail_info['shared'], dims=THUMBNAIL_DIMS)
    attachments = [item['encoded'] for item in mail_info['shared']]
    info('thumbnails downloaded and encoded as attachments')

    cnt = 0
    addrs = mail_info['to']
    for (email, email_id) in addrs.items():
        mail_info['email_id'] = email_id
        text_message = render_template(body_text_tmpl, mail_info)

        msg = EmailMultiAlternatives(
            from_email=DEFAULT_FROM_ADDRESS,
            to=[email],
            reply_to=[mail_info['from']],
            bcc=mail_info['to'],
            subject=mail_info['subject'],
            attachments=attachments,
            body=text_message,
        )

        html_message = render_template(body_html_tmpl, mail_info)
        msg.attach_alternative(html_message, 'text/html')

        msg.send()
        cnt = cnt + 1

        info(f'Message sent to {email}')
    info(f'{cnt} emails sent')
