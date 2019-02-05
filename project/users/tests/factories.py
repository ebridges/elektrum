from django.contrib.auth import get_user_model

from factory.django import DjangoModelFactory
from factory import Sequence
from pytest_factoryboy import register


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = Sequence(lambda n: "user%03d@example.com" % n)
    username = Sequence(lambda n: "user%03d" % n)
    first_name = Sequence(lambda n: "fname: %03d" % n)
    last_name = Sequence(lambda n: "lname: %03d" % n)


register(UserFactory)
