import pytest

from django.contrib.auth import get_user_model

from base.tests import util
from collection.models import Collection


@pytest.mark.django_db
def test_view_collection_unauthenticated(authenticated_client):
    """
    View a collection
    """
    (c, __) = authenticated_client
    colln_path = '/4041'
    r = util.create_collection(c, colln_path=colln_path)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path=colln_path)
    c.logout()
    r = c.get('/collections/view/%s' % colln.id)
    assert r.status_code == 403


@pytest.mark.django_db
def test_view_collection(authenticated_client):
    """
    View a collection
    """
    (c, __) = authenticated_client
    colln_path = '/4040'
    r = util.create_collection(c, colln_path=colln_path)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path=colln_path)
    r = c.get('/collections/view/%s' % colln.id)
    util.assert_contains(r, '<h2>Collection: %s</h2>' % colln_path)


@pytest.mark.django_db
def test_create_collection(authenticated_client):
    """
    Create a collection
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)


@pytest.mark.django_db
def test_create_collection_invalid_paths(authenticated_client):
    """
    Create collections with invalid paths, expect failures
    """
    (c, __) = authenticated_client
    invalid_path_msg = '<li>Enter a valid collection path. This value may only be a 4 digit year, ' \
                       'with a leading slash.</li>'

    r = util.create_collection(c, '/asdfasdf')
    util.assert_contains(r, invalid_path_msg)

    r = util.create_collection(c, 'asdf')
    util.assert_contains(r, invalid_path_msg)

    r = util.create_collection(c, '3030')
    util.assert_contains(r, invalid_path_msg)

    r = util.create_collection(c, None)
    util.assert_contains(r, invalid_path_msg)


@pytest.mark.django_db
def test_create_collection_missing_paths(authenticated_client):
    """
    Create a collection with missing path, expect failure
    """
    missing_path_msg = '<li>This field is required.</li>'
    (c, __) = authenticated_client
    r = util.create_collection(c, '')
    util.assert_contains(r, missing_path_msg)


@pytest.mark.django_db
def test_create_collection_duplicate_paths(authenticated_client):
    """
    Create a collection with duplicate path, expect failure
    """
    duplicate_path_msg = 'There exists already a path with name'
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    r = util.create_collection(c)
    util.assert_contains(r, duplicate_path_msg)


@pytest.mark.django_db
def test_edit_collection(authenticated_client):
    """
    Edit a collection
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    assert colln is not None
    r = c.post('/collections/edit/%s' % colln.id, {'path': '/3031'})
    colln = Collection.objects.filter(path='/3031')
    assert colln.exists()
    util.assert_account_redirects(r)


@pytest.mark.django_db
def test_edit_nonexistent_collection(authenticated_client):
    """
    Edit a collection that doesn't exist
    """
    (c, __) = authenticated_client
    nonexistent_colln_id = '91cf609b-1ed9-44fd-b478-09f083ce2b36'
    r = c.post('/collections/edit/%s' % nonexistent_colln_id, {'path': '/3031'})
    assert r.status_code == 404
    colln = Collection.objects.filter(path='/3031')
    assert not colln.exists()


@pytest.mark.django_db
def test_delete_collection(authenticated_client):
    """
    Delete a collection
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    r = c.post('/collections/delete/%s' % colln.id)
    util.assert_account_redirects(r)
    colln = Collection.objects.filter(path='/3030')
    assert not colln.exists()


@pytest.mark.django_db
def test_delete_collection_confirmation(authenticated_client):
    """
    Confirm deletion of a collection
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    r = c.get('/collections/delete/%s' % colln.id)
    util.assert_contains(r, 'Are you sure you want to delete')


@pytest.mark.django_db
def test_delete_user_confirm_collection_deleted(authenticated_client):
    """
    Delete a user and confirm collection is deleted
    """
    (c, u) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    user_model = get_user_model()
    user = user_model.objects.get(email=u.email)
    assert user is not None
    colln = Collection.objects.filter(path='/3030')
    assert colln.count() == 1
    user.delete()
    user.save()
    colln = Collection.objects.filter(path='/3030')
    assert colln.count() == 0


@pytest.mark.django_db
def test_create_collection_unauthenticated(client):
    """
    Attempt to create a collection when not authenticated, expect failure
    """
    r = util.create_collection(client)
    assert r.status_code == 403


@pytest.mark.django_db
def test_list_collection_unauthenticated(authenticated_client):
    """
    Attempt to list a collection when not authenticated, expect failure
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    c.logout()
    r = c.get('/collections/')
    assert r.status_code == 403


@pytest.mark.django_db
def test_delete_collection_unauthenticated(authenticated_client):
    """
    Attempt to delete a collection when not authenticated, expect failure
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    c.logout()
    r = c.post('/collections/delete/%s' % colln.id)
    assert r.status_code == 403


@pytest.mark.django_db
def test_edit_collection_unauthenticated(authenticated_client):
    """
    Attempt to edit a collection when not authenticated, expect failure
    """
    (c, __) = authenticated_client
    r = util.create_collection(c)
    util.assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    c.logout()
    r = c.post('/collections/edit/%s' % colln.id, {'path': '/3031'})
    assert r.status_code == 403
