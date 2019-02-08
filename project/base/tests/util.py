import email
import json
import os
import re

from urllib.parse import urljoin, urlsplit

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import QueryDict
from django.http.request import split_domain_port, validate_host
from django.test import Client, TestCase
from django.test.html import HTMLParseError, parse_html


def trunc_file(filename):
    with open(filename, 'w') as f:
        f.truncate()


def assert_signup_mail(email_to, email_log, email_subject_substr='Confirm'):
    url_pattern = re.compile(r'(https?://[^/]+/account/confirm-email/[^/]+/)')
    # subj_pattern = re.compile(r'\s+%s\s+' % email_subject_substr)

    confirm_url = None
    with open(email_log, 'rb') as fp:
        msg = email.message_from_binary_file(fp)
        assert msg['To'] == email_to
        assert email_subject_substr in msg['Subject']

    for i, line in enumerate(open(email_log)):
        match = re.search(url_pattern, line)
        if match:
            confirm_url = match.group(0)
            break

    return confirm_url


def assert_account_redirects(response, expected_url='/collections/', expected_redirect_sc=302,
                                  expected_target_sc=200):
    assert_redirects(response, expected_url, expected_redirect_sc, expected_target_sc)


def create_collection(client, colln_path='/3030'):
    response = client.post('/collections/new', {'path': colln_path})
    assert response is not None
    return response


# Not used!
def assert_redirect_contains(response, text, path='/collections/'):
    redirect_response = response.client.get(path, QueryDict())
    assert_contains(redirect_response, text)


def assert_and_parse_html(html, user_msg, msg):
    try:
        return parse_html(html)
    except HTMLParseError as e:
        standard_msg = '%s\n%s' % (msg, e)
        fail('%s: %s' % (user_msg, standard_msg))


def assert_contains(response, text, count=None, status_code=200, html=False):
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
        content = assert_and_parse_html(content, None, "Response's content is not valid HTML:")
        text = assert_and_parse_html(text, None, "Second argument is not valid HTML:")

    real_count = content.count(text)

    if count is not None:
        assert real_count == count, \
            "Found %d instances of %s in response (expected %d)" \
            % (real_count, text_repr, count)
    else:
        assert real_count != 0, "Couldn't find %s in response" % text_repr


def assert_redirects(response, expected_url, status_code=302,
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
