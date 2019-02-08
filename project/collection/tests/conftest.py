from pytest_factoryboy import register

from collection.tests.factories import CollectionFactory
from users.tests.factories import UserFactory

register(UserFactory)
register(CollectionFactory)

pytest_plugins = [
     "users.tests.fixtures"
]
