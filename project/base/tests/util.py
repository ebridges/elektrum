import email
import json
import os
import re
import pytest

from urllib.parse import urljoin, urlsplit, urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import QueryDict
from django.http.request import split_domain_port, validate_host
from django.shortcuts import reverse
from django.test import Client, TestCase
from django.test.html import HTMLParseError, parse_html

UUID_REGEX = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'

USER_PASSWORD = 'temporary'
email_file_path = os.path.join(settings.BASE_DIR, 'sent_emails')
email_log = os.path.join(email_file_path, 'test_authn_user_flows.log')


class MockPostRequest:
    def __init__(self, user=None, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'POST'
        self.POST = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


class MockGetRequest:
    def __init__(self, user=None, args={}, csrf_cookie='abcdefghijklmnopqrstuvwxyz'):
        self.user = user
        self.method = 'GET'
        self.GET = args
        self.META = {}
        self.META['CSRF_COOKIE'] = csrf_cookie


def assert_post_with_args(client, url_name, args, expected_code):
    request_url = reverse(url_name, kwargs=args)
    response = client.post(request_url)
    assert response.status_code == expected_code
    return response


def match_image_key(user_id, to_match):
    pattern = r'[/]?(?P<user_id>%s)/(?P<image_id>%s)\.(?P<extension>[a-z]{3})' % (
        user_id,
        UUID_REGEX,
    )
    return re.match(pattern, to_match)


def util_login_user(driver, live_server_url, user_email, password):
    u = urlparse(live_server_url)
    url = 'https://%s:%s/' % (u.hostname, u.port)
    driver.get(url)
    username_input = driver.find_element_by_name('login')
    username_input.send_keys(user_email)
    password_input = driver.find_element_by_name('password')
    password_input.send_keys(password)
    driver.find_element_by_xpath('//button').click()


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


def fail(msg):
    __tracebackhide__ = True
    pytest.fail(msg)
