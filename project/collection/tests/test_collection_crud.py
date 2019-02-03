import json

from urllib.parse import urljoin, urlsplit

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import QueryDict
from django.http.request import split_domain_port, validate_host
from django.test import Client, TestCase
from django.test.html import HTMLParseError, parse_html

from collection.models import Collection

import pytest


def util_assert_account_redirects(response, expected_url='/collections/', expected_redirect_sc=302,
                                  expected_target_sc=200):
    util_assert_redirects(response, expected_url, expected_redirect_sc, expected_target_sc)


def util_authenticated_client(test_data):
    client = Client()
    login_result = client.login(email=test_data[0]['fields']['email'],
                                password=test_data[0]['fields']['password_plaintext'])
    assert login_result
    return client


def util_create_collection(client, colln_path='/3030'):
    response = client.post('/collections/new', {'path': colln_path})
    assert response is not None
    return response


# Not used!
def util_assert_redirect_contains(response, text, path='/collections/'):
    redirect_response = response.client.get(path, QueryDict())
    util_assert_contains(redirect_response, text)


def util_assert_and_parse_html(html, user_msg, msg):
    try:
        return parse_html(html)
    except HTMLParseError as e:
        standard_msg = '%s\n%s' % (msg, e)
        fail('%s: %s' % (user_msg, standard_msg))


def util_assert_contains(response, text, count=None, status_code=200, html=False):
    """
    Assert that a response indicates that some content was retrieved
    successfully, (i.e., the HTTP status code was as expected) and that
    ``text`` occurs ``count`` times in the content of the response.
    If ``count`` is None, the count doesn't matter - the assertion is true
    if the text occurs at least once in the response.
    """

    # If the response supports deferred rendering and hasn't been rendered
    # yet, then ensure that it does get rendered before proceeding further.
    if hasattr(response, 'render') and callable(response.render) and not response.is_rendered:
        response.render()

    assert response.status_code == status_code, \
        "Couldn't retrieve content: Response code was %d (expected %d)" \
        % (response.status_code, status_code)

    if response.streaming:
        content = b''.join(response.streaming_content)
    else:
        content = response.content
    if not isinstance(text, bytes) or html:
        text = str(text)
        content = content.decode(response.charset)
        text_repr = "'%s'" % text
    else:
        text_repr = repr(text)
    if html:
        content = util_assert_and_parse_html(content, None, "Response's content is not valid HTML:")
        text = util_assert_and_parse_html(text, None, "Second argument is not valid HTML:")

    real_count = content.count(text)

    if count is not None:
        assert real_count == count, \
            "Found %d instances of %s in response (expected %d)" \
            % (real_count, text_repr, count)
    else:
        assert real_count != 0, "Couldn't find %s in response" % text_repr


def util_assert_redirects(response, expected_url, status_code=302,
                          target_status_code=200, fetch_redirect_response=True):
    """
    Assert that a response redirected to a specific URL and that the
    redirect URL can be loaded.

    Won't work for external links since it uses the test client to do a
    request (use fetch_redirect_response=False to check such links without
    fetching them).
    """

    if hasattr(response, 'redirect_chain'):
        # The request was a followed redirect
        assert response.redirect_chain, \
            "Response didn't redirect as expected: Response code was %d (expected %d)" \
            % (response.status_code, status_code)

        assert response.redirect_chain[0][1] == status_code, \
            "Initial response didn't redirect as expected: Response code was %d (expected %d)" \
            % (response.redirect_chain[0][1], status_code)

        url, status_code = response.redirect_chain[-1]
        #        scheme, netloc, path, query, fragment = urlsplit(url)

        assert response.status_code == target_status_code, \
            "Response didn't redirect as expected: Final Response code was %d (expected %d)" \
            % (response.status_code, target_status_code)

    else:
        # Not a followed redirect
        assert response.status_code == status_code, \
            "Response didn't redirect as expected: Response code was %d (expected %d)" \
            % (response.status_code, status_code)

        url = response.url
        scheme, netloc, path, query, fragment = urlsplit(url)

        # Prepend the request path to handle relative path redirects.
        if not path.startswith('/'):
            url = urljoin(response.request['PATH_INFO'], url)
            path = urljoin(response.request['PATH_INFO'], path)

        if fetch_redirect_response:
            # netloc might be empty, or in cases where Django tests the
            # HTTP scheme, the convention is for netloc to be 'testserver'.
            # Trust both as "internal" URLs here.
            domain, port = split_domain_port(netloc)
            if domain and not validate_host(domain, settings.ALLOWED_HOSTS):
                raise ValueError(
                    "The test client is unable to fetch remote URLs (got %s). "
                    "If the host is served by Django, add '%s' to ALLOWED_HOSTS. "
                    "Otherwise, use assertRedirects(..., fetch_redirect_response=False)."
                    % (url, domain)
                )
            redirect_response = response.client.get(path, QueryDict(query), secure=(scheme == 'https'))

            # Get the redirection page, using the same client that was used
            # to obtain the original response.
            assert redirect_response.status_code == target_status_code, \
                "Couldn't retrieve redirection page '%s': response code was %d (expected %d)" \
                % (path, redirect_response.status_code, target_status_code)

    assert url == expected_url, \
        "Response redirected to '%s', expected '%s'" % (url, expected_url)


def fail(msg):
    __tracebackhide__ = True
    pytest.fail(msg)


# ############### Tests Begin

@pytest.mark.django_db
def test_view_collection_unauthenticated(test_data):
    """
    View a collection
    """
    colln_path = '/4041'
    c = util_authenticated_client(test_data)
    r = util_create_collection(c, colln_path=colln_path)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path=colln_path)
    c.logout()
    r = c.get('/collections/view/%s' % colln.id)
    assert r.status_code == 403


@pytest.mark.django_db
def test_view_collection(test_data):
    """
    View a collection
    """
    colln_path = '/4040'
    c = util_authenticated_client(test_data)
    r = util_create_collection(c, colln_path=colln_path)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path=colln_path)
    r = c.get('/collections/view/%s' % colln.id)
    util_assert_contains(r, '<h2>Collection: %s</h2>' % colln_path)


@pytest.mark.django_db
def test_create_collection(test_data):
    """
    Create a collection
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)


@pytest.mark.django_db
def test_create_collection_invalid_paths(test_data):
    """
    Create collections with invalid paths, expect failures
    """
    invalid_path_msg = '<li>Enter a valid collection path. This value may only be a 4 digit year, '    'with a leading slash.</li>'
    c = util_authenticated_client(test_data)

    r = util_create_collection(c, '/asdfasdf')
    util_assert_contains(r, invalid_path_msg)

    r = util_create_collection(c, 'asdf')
    util_assert_contains(r, invalid_path_msg)

    r = util_create_collection(c, '3030')
    util_assert_contains(r, invalid_path_msg)

    r = util_create_collection(c, None)
    util_assert_contains(r, invalid_path_msg)


@pytest.mark.django_db
def test_create_collection_missing_paths(test_data):
    """
    Create a collection with missing path, expect failure
    """
    missing_path_msg = '<li>This field is required.</li>'
    c = util_authenticated_client(test_data)
    r = util_create_collection(c, '')
    util_assert_contains(r, missing_path_msg)


@pytest.mark.django_db
def test_create_collection_duplicate_paths(test_data):
    """
    Create a collection with duplicate path, expect failure
    """
    duplicate_path_msg = 'There exists already a path with name'
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    r = util_create_collection(c)
    util_assert_contains(r, duplicate_path_msg)


@pytest.mark.django_db
def test_edit_collection(test_data):
    """
    Edit a collection
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    assert colln is not None
    r = c.post('/collections/edit/%s' % colln.id, {'path': '/3031'})
    colln = Collection.objects.filter(path='/3031')
    assert colln.exists()
    util_assert_account_redirects(r)


@pytest.mark.django_db
def test_edit_nonexistent_collection(test_data):
    """
    Edit a collection that doesn't exist
    """
    c = util_authenticated_client(test_data)
    nonexistent_colln_id = '91cf609b-1ed9-44fd-b478-09f083ce2b36'
    r = c.post('/collections/edit/%s' % nonexistent_colln_id, {'path': '/3031'})
    assert r.status_code == 404
    colln = Collection.objects.filter(path='/3031')
    assert not colln.exists()


@pytest.mark.django_db
def test_delete_collection(test_data):
    """
    Delete a collection
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    r = c.post('/collections/delete/%s' % colln.id)
    util_assert_account_redirects(r)
    colln = Collection.objects.filter(path='/3030')
    assert not colln.exists()


@pytest.mark.django_db
def test_delete_collection_confirmation(test_data):
    """
    Confirm deletion of a collection
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    r = c.get('/collections/delete/%s' % colln.id)
    util_assert_contains(r, 'Are you sure you want to delete')


@pytest.mark.django_db
def test_delete_user_confirm_collection_deleted(test_data):
    """
    Delete a user and confirm collection is deleted
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    user_model = get_user_model()
    user = user_model.objects.get(email=test_data[0]['fields']['email'])
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
    r = util_create_collection(client)
    assert r.status_code == 403


@pytest.mark.django_db
def test_list_collection_unauthenticated(test_data):
    """
    Attempt to list a collection when not authenticated, expect failure
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    c.logout()
    r = c.get('/collections/')
    assert r.status_code == 403


@pytest.mark.django_db
def test_delete_collection_unauthenticated(test_data):
    """
    Attempt to delete a collection when not authenticated, expect failure
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    c.logout()
    r = c.post('/collections/delete/%s' % colln.id)
    assert r.status_code == 403


@pytest.mark.django_db
def test_edit_collection_unauthenticated(test_data):
    """
    Attempt to edit a collection when not authenticated, expect failure
    """
    c = util_authenticated_client(test_data)
    r = util_create_collection(c)
    util_assert_account_redirects(r)
    colln = Collection.objects.get(path='/3030')
    c.logout()
    r = c.post('/collections/edit/%s' % colln.id, {'path': '/3031'})
    assert r.status_code == 403
