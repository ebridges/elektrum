import re
import os
import json
import email

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import Client, TestCase

from collection.models import Collection

class CollectionTest(TestCase):
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
    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)


  def test_create_collection_invalid_paths(self):
    '''
    Create collections with invalid paths, expect failures
    '''
    invalid_path_msg='<li>Enter a valid collection path. This value may only be a 4 digit year, with a leading slash.</li>'

    c = self.util_authenticated_client()

    r = self.util_create_collection(c, '/asdfasdf')
    self.assertContains(r, invalid_path_msg)

    r = self.util_create_collection(c, 'asdf')
    self.assertContains(r, invalid_path_msg)

    r = self.util_create_collection(c, '3030')
    self.assertContains(r, invalid_path_msg)

    r = self.util_create_collection(c, None)
    self.assertContains(r, invalid_path_msg)


  def test_create_collection_missing_paths(self):
    '''
    Create a collection with missing path, expect failure
    '''
    missing_path_msg='<li>This field is required.</li>'

    c = self.util_authenticated_client()

    r = self.util_create_collection(c, '')
    self.assertContains(r, missing_path_msg)


  def test_create_collection_duplicate_paths(self):
    '''
    Create a collection with duplicate path, expect failure
    '''
    duplicate_path_msg='<li>A collection with that path already exists.</li>'

    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)

    r = self.util_create_collection(c)
    self.assertContains(r, duplicate_path_msg)


  def test_delete_user_confirm_collection_deleted(self):
    '''
    Delete a user and confirm collection is deleted
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)

    user_model = get_user_model()

    user = user_model.objects.get(email=self.data[0]['fields']['email'])
    self.assertIsNotNone(user)

    colln = Collection.objects.filter(path='/3030')
    self.assertEqual(colln.count(), 1)

    user.delete()
    user.save()

    colln = Collection.objects.filter(path='/3030')
    self.assertEqual(colln.count(), 0)



# attempt to list/edit/create/delete a collection when not authenticated (user#is_authenticated is False), expect failure
# attempt to list/edit/create/delete another user's collection, expect failure

  def util_assert_account_redirects(self, response, expected_url='/collections/', expected_redirect_sc=302, expected_target_sc=200):
    self.assertRedirects(response, expected_url, expected_redirect_sc, expected_target_sc)

  def util_authenticated_client(self):
    c = Client()
    login_result = c.login(email=self.data[0]['fields']['email'], password=self.password)
    self.assertTrue(login_result)
    return c

  def util_create_collection(self, client, colln_path='/3030'):
    response = client.post('/collections/new', {'path': colln_path})
    self.assertIsNotNone(response)
    return response

  def util_assert_redirect_contains(self, response, text, path='/collections/'):
    redirect_response = response.client.get(path, QueryDict())
    self.assertContains(redirect_response, text)
