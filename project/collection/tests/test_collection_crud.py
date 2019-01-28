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


  def test_view_collection_unauthenticated(self):
    '''
    View a collection
    '''
    colln_path='/4041'

    c = self.util_authenticated_client()
    r = self.util_create_collection(c, colln_path=colln_path)
    self.util_assert_account_redirects(r)

    colln = Collection.objects.get(path=colln_path)
    c.logout()

    r = c.get('/collections/view/%s' % colln.id)
    self.assertEqual(r.status_code, 403)


  def test_view_collection(self):
    '''
    View a collection
    '''
    colln_path='/4040'

    c = self.util_authenticated_client()
    r = self.util_create_collection(c, colln_path=colln_path)
    self.util_assert_account_redirects(r)

    colln = Collection.objects.get(path=colln_path)
    r = c.get('/collections/view/%s' % colln.id)
    self.assertContains(r, '<h2>Collection: %s</h2>' % colln_path)    


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
    duplicate_path_msg='There exists already a path with name'
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)

    r = self.util_create_collection(c)
    self.assertContains(r, duplicate_path_msg)


  def test_edit_collection(self):
    '''
    Edit a collection
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    self.assertIsNotNone( colln )

    r = c.post('/collections/edit/%s' % colln.id, {'path':'/3031'})
    colln = Collection.objects.filter(path='/3031')
    self.assertTrue( colln.exists() )

    self.util_assert_account_redirects(r)


  def test_edit_nonexistent_collection(self):
    '''
    Edit a collection that doesn't exist
    '''
    c = self.util_authenticated_client()

    nonexistent_colln_id='91cf609b-1ed9-44fd-b478-09f083ce2b36'
    r = c.post('/collections/edit/%s' % nonexistent_colln_id, {'path':'/3031'})
    self.assertEqual(r.status_code, 404)

    colln = Collection.objects.filter(path='/3031')
    self.assertFalse( colln.exists() )


  def test_delete_collection(self):
    '''
    Delete a collection
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')

    r = c.post('/collections/delete/%s' % colln.id)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.filter(path='/3030')
    self.assertFalse( colln.exists() )


  def test_delete_collection_confirmation(self):
    '''
    Confirm deletion of a collection
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')

    r = c.get('/collections/delete/%s' % colln.id)
    self.assertContains(r, 'Are you sure you want to delete')


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


  def test_create_collection_unauthenticated(self):
    '''
    Attempt to create a collection when not authenticated, expect failure
    '''
    c = Client()
    r = self.util_create_collection(c)
    self.assertEqual(r.status_code, 403)


  def test_list_collection_unauthenticated(self):
    '''
    Attempt to list a collection when not authenticated, expect failure
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)

    c.logout()

    r = c.get('/collections/')
    self.assertEquals(r.status_code, 403)


  def test_delete_collection_unauthenticated(self):
    '''
    Attempt to delete a collection when not authenticated, expect failure
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')

    c.logout()

    r = c.post('/collections/delete/%s' % colln.id)
    self.assertEquals(r.status_code, 403)


  def test_edit_collection_unauthenticated(self):
    '''
    Attempt to edit a collection when not authenticated, expect failure
    '''
    c = self.util_authenticated_client()

    r = self.util_create_collection(c)
    self.util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')

    c.logout()

    r = c.post('/collections/edit/%s' % colln.id, {'path':'/3031'})
    self.assertEquals(r.status_code, 403)


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
