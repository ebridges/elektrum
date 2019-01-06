from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(blank=False, null=False, unique=True, max_length=512, verbose_name='email address')
    first_name = models.CharField(blank=False, null=False, max_length=255, verbose_name='first name')
    last_name = models.CharField(blank=False, null=False, max_length=255, verbose_name='last name')
    ### [#13]: do not require username
    username = models.CharField(
        _('username'),
        null=True,
        max_length=150,
        unique=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    def __str__(self):
        return '%s %s <%s>' % (self.first_name, self.last_name, self.email)
