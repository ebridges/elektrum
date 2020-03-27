from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def send_email(
    sender, to, subject, body_text_tmpl=None, body_html_tmpl=None, context={}, attachments=[]
):
    '''
  Attachments: an array of https://docs.python.org/3.8/library/email.mime.html#email.mime.image.MIMEImage
  '''
    headers = {}

    html = get_template(body_html_tmpl)
    html_message = html.render(context)

    if body_text_tmpl:
        plaintext = get_template(body_text_tmpl)
        text_message = plaintext.render(context)

    msg = EmailMultiAlternatives(
        from_email=sender,
        to=[sender],
        reply_to=[sender],
        bcc=to,
        subject=subject,
        body=html_message,
        attachments=attachments,
        headers=headers,
    )

    if body_text_tmpl:
        msg.attach_alternative(text_message, 'text/plain')

    msg.send()
