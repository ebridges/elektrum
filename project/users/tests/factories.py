import os

from django.core.mail.backends.filebased import EmailBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from factory.django import DjangoModelFactory
from factory import Sequence
from pytest_factoryboy import register

from base.tests.util import USER_PASSWORD, email_log


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = Sequence(lambda n: "user%03d@example.com" % n)
    username = Sequence(lambda n: "user%03d" % n)
    first_name = Sequence(lambda n: "fname: %03d" % n)
    last_name = Sequence(lambda n: "lname: %03d" % n)
    password = make_password(USER_PASSWORD)


class MyEmailBackend(EmailBackend):
    def _get_filename(self):
        self._fname = email_log
        return self._fname
