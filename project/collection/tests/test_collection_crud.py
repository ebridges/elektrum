import re
import os
import json
import email

from django.test import Client, TestCase


class AuthnUserFlowTest(TestCase):
  fixtures = ['users/tests/user-data.json']

  def setUp(self):
    self.email_log_dir = './sent_emails'
    self.password='temporary'
    with open('users/tests/user-data.json') as f:
        d = json.load(f)
        self.data=d

  def test_signup_flow(self):
    c = Client()
    response = c.post('/account/signup/', {'username': 'newuser', 'email': 'newuser@example.com', 'first_name': 'first', 'last_name': 'last', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)
