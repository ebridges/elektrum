import hashlib

from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

from base.models import BaseModel


class CustomUser(AbstractUser, BaseModel):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        blank=False, null=False, unique=True, max_length=512, verbose_name='email address'
    )
    first_name = models.CharField(
        blank=False, null=False, max_length=255, verbose_name='first name'
    )
    last_name = models.CharField(blank=False, null=False, max_length=255, verbose_name='last name')
    username = models.CharField(
        _('username'),
        null=False,
        max_length=150,
        unique=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={'unique': _('A user with that username already exists.')},
    )
    shared_items = models.ManyToManyField(
        'media_items.MediaItem', through='sharing.Share', related_name='shared_items'
    )

    def is_account_verified(self):
        if self.is_authenticated:
            result = EmailAddress.objects.filter(email=self.email)
            if len(result):
                return result[0].verified
        return False

    def profile_image_url(self):  # pragma: no cover
        gogl_acct = SocialAccount.objects.filter(user_id=self.id, provider='google')

        if len(gogl_acct):
            return gogl_acct[0].extra_data['picture']

        return 'http://www.gravatar.com/avatar/{}?s=40'.format(
            hashlib.md5(self.email.encode('utf-8')).hexdigest()
        )

    def __str__(self):
        return '%s %s <%s>' % (self.first_name, self.last_name, self.email)
