import re
import os
import json
import email

from django.test import Client, TestCase


class AuthnUserFlowTest(TestCase):
  fixtures = ['users/tests/user-data.json']

  def setUp(self):
    self.password='temporary'
    with open('users/tests/user-data.json') as f:
        d = json.load(f)
        self.data=d

  # create a collection
  def test_create_collection(self):
    c = Client()
    c.login(email=self.data[0]['fields']['email'], password=self.data[0]['fields']['password'])
    response = c.post('', {'path': '/3030'})
    self.assertIsNotNone(response)

# create a collection with invalid path, expect failure
# create a collection with missing path, expect failure
# create a collection with duplicate path, expect failure
# delete a user and confirm collection is deleted
# attempt to list/edit/create/delete a collection when not authenticated (user#is_authenticated is False), expect failure
# attempt to list/edit/create/delete another user's collection, expect failure
