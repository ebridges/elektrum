from pytest_factoryboy import register

from collection.tests.factories import CollectionFactory


register(CollectionFactory)

pytest_plugins = [
     "base.tests.fixtures"
]
