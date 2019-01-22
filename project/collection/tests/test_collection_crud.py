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

  def test_create_collection(self):
    '''
    Create a collection
    '''
    c = Client()
    login_result = c.login(email=self.data[0]['fields']['email'], password=self.password)
    self.assertTrue(login_result)
    response = c.post('/collections/new', {'path': '/3030'})
    self.assertIsNotNone(response)
    self.util_assert_account_redirects(response)


# create a collection with invalid path, expect failure
# create a collection with missing path, expect failure
# create a collection with duplicate path, expect failure
# delete a user and confirm collection is deleted
# attempt to list/edit/create/delete a collection when not authenticated (user#is_authenticated is False), expect failure
# attempt to list/edit/create/delete another user's collection, expect failure

  def util_assert_account_redirects(self, response, expected_url='/collections/', expected_redirect_sc=302, expected_target_sc=200):
    self.assertRedirects(response, expected_url, expected_redirect_sc, expected_target_sc)
