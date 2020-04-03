from django.core.mail import EmailMultiAlternatives

from emailer.utils import download_and_encode_thumbnails, render_template


def send_email(sender, to, subject, body_text_tmpl=None, body_html_tmpl=None, context={}):

    download_and_encode_thumbnails(context['owner_id'], context['objects'])
    attachments = [item['encoded'] for item in context['objects']]

    msg = EmailMultiAlternatives(
        from_email=sender,
        to=[sender],
        reply_to=[sender],
        bcc=to,
        subject=subject,
        attachments=attachments,
    )

    html_message = render_template(body_html_tmpl, context)
    msg.attach_alternative(html_message, 'text/html')

    msg.content_subtype = 'html'

    if body_text_tmpl:
        text_message = render_template(body_text_tmpl, context)
        msg.attach_alternative(text_message, 'text/plain')

    msg.send()
