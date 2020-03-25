from django import forms
from django.forms import fields, widgets
from django.utils.translation import gettext_lazy as _
from sharing.fields import MultiEmailField
import uuid


class ShareForm(forms.Form):
    from_address = fields.EmailField(
        label=_('From'),
        help_text=_('Return & reply-to address for the email.'),
        disabled=True,
        required=False,
        widget=forms.EmailInput(attrs={'id': 'from-address', 'size': 64}),
    )
    to_address = MultiEmailField(
        label=_('Share To'),
        help_text=_('Enter one or more email addresses, separated by commas.'),
        required=False,
        error_messages={
            'required': _('Please enter at least one email address.'),
            'invalid_email': _('Invalid email address: [%(value)s]'),
            'invalid_emails': _('Invalid email addresses: [%(value)s]'),
        },
        widget=forms.EmailInput(
            attrs={
                'id': 'to-address',
                'multiple': 'true',
                'size': 128,
                'minlength': 3,
                'maxlength': 256,
                'list': 'default-emails',
                'placeholder': _('joe@example.com, jane@example.com'),
            }
        ),
    )
    subject_line = fields.CharField(
        label=_('Subject'),
        help_text=_('Subject of the email.'),
        required=False,
        widget=forms.TextInput(
            attrs={'id': 'subject-line', 'size': 128, 'minlength': 3, 'maxlength': 256}
        ),
    )
    share_message = fields.CharField(
        label=_('Message'),
        help_text=_('Add a message to be included in the body of the email with the photos.'),
        required=False,
        widget=widgets.Textarea(
            attrs={
                'id': 'share-message',
                'placeholder': _('An optional message to accompany the photos.'),
                'cols': 132,
                'rows': 16,
            }
        ),
    )
