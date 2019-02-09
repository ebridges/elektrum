from factory.django import DjangoModelFactory
from factory import SubFactory
from pytest_factoryboy import register

from collection.models import Collection

from users.tests.factories import UserFactory


class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = Collection

    user = SubFactory(UserFactory)


register(UserFactory)
register(CollectionFactory)
