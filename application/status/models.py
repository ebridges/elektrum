from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel
from media_items.models import MediaItemPathValidator


class ProcessorLog(BaseModel):

    media_item_path_validator = MediaItemPathValidator()

    owner = models.ForeignKey(
        get_user_model(),
        help_text=_('Required. User that owns this media item'),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    event_date = models.DateTimeField(_('Event date.'), null=False, blank=False)

    file_path = models.CharField(
        _('file path'),
        help_text=_('Required. Path to media item from the root of users archive.'),
        null=False,
        blank=False,
        validators=[media_item_path_validator],
        max_length=4096,
    )

    error_code = models.CharField(
        _('Error code'),
        help_text=_('Required. Classification of the error.'),
        null=False,
        blank=False,
        max_length=64,
    )

    message = models.CharField(
        _('Error message'),
        help_text=_('Required. Error message.'),
        null=False,
        blank=False,
        max_length=4096,
    )

    reason = models.CharField(
        _('Error reason'),
        help_text=_('Optional. Reason for the error, e.g. stacktrace.'),
        null=True,
        blank=True,
        max_length=8192,
    )

    original_file_path = models.CharField(
        _('Original file path'),
        help_text=_('Optional. Path to media item that was uploaded.'),
        null=True,
        blank=True,
        max_length=4096,
    )


class ProcessorLogForm(forms.ModelForm):
    class Meta:
        model = ProcessorLog
        fields = '__all__'

    # event_date=widget=forms.DateTimeField(input_formats='%Y-%m-%dT%H:%M:%S')
