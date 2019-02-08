import os

from django.conf import settings
from django.core.mail.backends.filebased import EmailBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from factory.django import DjangoModelFactory
from factory import Sequence
from pytest_factoryboy import register


USER_PASSWORD = 'temporary'


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = Sequence(lambda n: "user%03d@example.com" % n)
    username = Sequence(lambda n: "user%03d" % n)
    first_name = Sequence(lambda n: "fname: %03d" % n)
    last_name = Sequence(lambda n: "lname: %03d" % n)
    password = make_password(USER_PASSWORD)


email_file_path = os.path.join(settings.BASE_DIR, 'sent_emails')
email_log = os.path.join(email_file_path, 'test_authn_user_flows.log')


class MyEmailBackend(EmailBackend):
    def _get_filename(self):
        self._fname = email_log
        return self._fname
