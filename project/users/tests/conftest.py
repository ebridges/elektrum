from pytest_factoryboy import register

from users.tests.factories import UserFactory

register(UserFactory)

pytest_plugins = [
     "users.tests.fixtures"
]
