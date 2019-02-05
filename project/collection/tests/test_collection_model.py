from django.core.exceptions import ValidationError

import pytest

from collection.models import Collection, CollectionPathValidator


@pytest.mark.django_db
def test_name_from_path(collection_factory):
    """
    Confirm correct name as derived from path.
    """
    c = collection_factory(path='/3030')
    assert c.name() == '3030'


@pytest.mark.django_db
def test_model_create_valid_path(collection_factory):
    """
    Create a model instance with a valid path.
    """
    c = collection_factory(path='/3030')
    assert c.path == '/3030'


@pytest.mark.django_db
def test_model_create_unique(collection_factory):
    """
    Confirm two collections with same name for user cannot be created.
    """
    colln = Collection.objects.filter(path='/4040')
    assert not colln.exists()

    c1 = collection_factory(path='/4040')

    colln = Collection.objects.filter(path='/4040')
    assert colln.exists()

    with pytest.raises(ValidationError):
        c1.validate_unique(None)


def test_model_valid_pathname():
    """
    Confirm that a valid pathname passes validation.
    """
    pathname = '/9999'
    assert Collection.collection_path_validator(pathname) is None
    validator = CollectionPathValidator()
    assert validator(pathname) is None


def test_model_invalid_pathname():
    """
    Confirm that an invalid pathname fails validation.
    """
    pathname = 'abcd'
    with pytest.raises(ValidationError):
        Collection.collection_path_validator(pathname)
