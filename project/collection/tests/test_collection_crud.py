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
    c = self.util_authenticated_client()

    response = c.post('/collections/new', {'path': '/3030'})
    self.assertIsNotNone(response)
    self.util_assert_account_redirects(response)


  def test_create_collection_invalid_paths(self):
    '''
    Create collections with invalid paths, expect failures
    '''
    c = self.util_authenticated_client()

    invalid_path_msg='<li>Enter a valid collection path. This value may only be a 4 digit year, with a leading slash.</li>'

    response = c.post('/collections/new', {'path': '/asdfasdf'})
    self.assertIsNotNone(response)
    self.assertContains(response, invalid_path_msg)

    response = c.post('/collections/new', {'path': 'asdf'})
    self.assertIsNotNone(response)
    self.assertContains(response, invalid_path_msg)

    response = c.post('/collections/new', {'path': '3030'})
    self.assertIsNotNone(response)
    self.assertContains(response, invalid_path_msg)


  def test_create_collection_missing_paths(self):
    '''
    Create a collection with missing path, expect failure
    '''
    c = self.util_authenticated_client()

    missing_path_msg='<li>This field is required.</li>'
    
    response = c.post('/collections/new', {'path': ''})
    self.assertIsNotNone(response)
    self.assertContains(response, missing_path_msg)


  def test_create_collection_duplicate_paths(self):
    '''
    Create a collection with duplicate path, expect failure
    '''
    c = self.util_authenticated_client()

    duplicate_path_msg='<li>A collection with that path already exists.</li>'

    response = c.post('/collections/new', {'path': '/3030'})
    self.assertIsNotNone(response)
    self.util_assert_account_redirects(response)

    response = c.post('/collections/new', {'path': '/3030'})
    self.assertIsNotNone(response)
    self.assertContains(response, duplicate_path_msg)



# delete a user and confirm collection is deleted
# attempt to list/edit/create/delete a collection when not authenticated (user#is_authenticated is False), expect failure
# attempt to list/edit/create/delete another user's collection, expect failure

  def util_assert_account_redirects(self, response, expected_url='/collections/', expected_redirect_sc=302, expected_target_sc=200):
    self.assertRedirects(response, expected_url, expected_redirect_sc, expected_target_sc)

  def util_authenticated_client(self):
    c = Client()
    login_result = c.login(email=self.data[0]['fields']['email'], password=self.password)
    self.assertTrue(login_result)
    return c
