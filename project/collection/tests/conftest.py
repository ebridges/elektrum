import pytest
import pathlib
import json

import pytest

from django.core.management import call_command

from pytest_factoryboy import register

from collection.tests.factories import CollectionFactory

register(CollectionFactory)


@pytest.fixture(scope='session')
def data_file(request):
    f = pathlib.Path(request.node.fspath.strpath)
    print("\nCurrent dir : %s" % f)
    config = f / 'users/tests/user-data.json'
    print("Test data file : %s" % config)
    assert config.exists()
    return config


@pytest.fixture(scope='session')
def django_db_setup(data_file, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', data_file)


@pytest.fixture(scope="module")
def test_data(data_file):
    with data_file.open() as fd:
        test_data = json.loads(fd.read())
    for item in test_data:
        item['fields']['password_plaintext'] = 'temporary'
    yield test_data
