from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.exceptions import ValidationError

from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory

from collection.models import Collection, CollectionPathValidator


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = Sequence(lambda n: "user%03d@example.com" % n)
    username = Sequence(lambda n: "user%03d" % n)
    first_name = Sequence(lambda n: "fname: %03d" % n)
    last_name = Sequence(lambda n: "lname: %03d" % n)


class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = Collection

    user = SubFactory(UserFactory)


class CollectionModelTest(TestCase):

    def test_name_from_path(self):
        """
        Confirm correct name as derived from path.
        """
        c = CollectionFactory(path='/3030')
        self.assertEqual(c.name(), '3030')

    def test_model_create_valid_path(self):
        """
        Create a model instance with a valid path.
        """
        c = CollectionFactory(path='/3030')
        self.assertEqual(c.path, '/3030')

    def test_model_valid_pathname(self):
        """
        Confirm that a valid pathname passes validation.
        """
        pathname = '/9999'
        self.assertIsNone(Collection.collection_path_validator(pathname))
        validator = CollectionPathValidator()
        self.assertIsNone(validator(pathname))

    def test_model_invalid_pathname(self):
        """
        Confirm that an invalid pathname fails validation.
        """
        pathname = 'abcd'
        with self.assertRaises(ValidationError):
            Collection.collection_path_validator(pathname)

    def test_model_create_unique(self):
        """
        Confirm two collections with same name for user cannot be created.
        """
        colln = Collection.objects.filter(path='/4040')
        self.assertFalse(colln.exists())

        c1 = CollectionFactory(path='/4040')

        colln = Collection.objects.filter(path='/4040')
        self.assertTrue(colln.exists())

        with self.assertRaises(ValidationError):
            c1.validate_unique(None)
