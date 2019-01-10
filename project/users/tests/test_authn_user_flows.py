import re
import os
import json
import email

from django.test import Client, TestCase, override_settings
from django.core.mail.backends.filebased import EmailBackend
from allauth.account.models import EmailAddress

from users.models import CustomUser

class AuthnUserFlowTest(TestCase):
  fixtures = ['users/tests/user-data.json']

  def setUp(self):
    self.email_log_dir = './sent_emails'
    self.password='temporary'
    with open('users/tests/user-data.json') as f:
        d = json.load(f)
        self.data=d[0]

  def test_login(self):
    c = Client()
    result = c.login(email=self.data['fields']['email'], password=self.password)
    self.assertTrue(result)

  def test_login_fail(self):
    c = Client()
    result = c.login(email=self.data['fields']['email'], password='wrong_password')
    self.assertFalse(result)

  def test_login_via_post(self):
    c = Client()
    response = c.post('/account/login/', {'login': self.data['fields']['email'], 'password': self.password})
    self.util_assert_account_redirects(response)
    user = CustomUser.objects.get(username=self.data['fields']['username'])
    self.assertEqual(response.context['user'].email, user.email)

  def test_csrf_login_failure(self):
    c = Client(enforce_csrf_checks=True)
    response = c.post('/account/login/', {'login': self.data['fields']['email'], 'password': 'wrong_password'})
    self.assertEqual(response.status_code, 403)

  def test_logout(self):
    c = Client()
    result = c.login(email=self.data['fields']['email'], password=self.password)
    self.assertTrue(result)
    response = c.post('/account/logout/')
    self.util_assert_account_redirects(response, expected_url='/')

  def test_csrf_logout_failure(self):
    c = Client(enforce_csrf_checks=True)
    response = c.post('/account/logout/')
    self.assertEqual(response.status_code, 403)

  @override_settings(EMAIL_BACKEND = 'users.tests.test_authn_user_flows.MyEmailBackend')
  def test_signup_flow(self):
    c = Client()
    response = c.post('/account/signup/', {'email': 'newuser@example.com', 'first_name': 'first', 'last_name': 'last', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)
    confirm_url = self.util_assert_signup_mail('newuser@example.com')
    self.assertIsNotNone(confirm_url)
    response = c.post(confirm_url)
    
    # Because `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION` is "True", the user is redirected to '/'
    # If there is some delay (see docs on that setting) then the redirect will be to '/account/login/'
    self.util_assert_account_redirects(response, expected_url='/')

    email = EmailAddress.objects.get(email='newuser@example.com')
    self.assertTrue(email.verified)


  @override_settings(EMAIL_BACKEND = 'users.tests.test_authn_user_flows.MyEmailBackend')
  def test_signup_flow_multiple(self):
    c = Client()
    response = c.post('/account/signup/', {'email': 'newuser2@example.com', 'first_name': 'first2', 'last_name': 'last2', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)
    self.util_assert_signup_mail('newuser2@example.com')

    response = c.post('/account/signup/', {'email': 'newuser3@example.com', 'first_name': 'first3', 'last_name': 'last3', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)
    self.util_assert_signup_mail('newuser3@example.com')

  def util_assert_account_redirects(self, response, expected_url='/account/confirm-email/', expected_redirect_sc=302, expected_target_sc=200):
    self.assertRedirects(response, expected_url, expected_redirect_sc, expected_target_sc)

  def util_assert_signup_mail(self, email_to, email_subject_substr='Confirm'):
    loc = os.path.join(self.email_log_dir, 'test_authn_user_flows.log')
    pattern = re.compile("(https?://[^/]+/account/confirm-email\/[^/]+/)")
    confirm_url = None
    try:
      with open(loc, 'rb') as fp:
        msg = email.message_from_binary_file(fp)
        self.assertEqual(msg['To'], email_to)
        self.assertRegex(msg['Subject'], '\s+%s\s+' % email_subject_substr)

      for i, line in enumerate(open(loc)):
        match = re.search(pattern, line)
        if match:
          confirm_url = match.group(0)
          break

    finally:
      if os.path.exists(loc):
        os.remove(loc)
    
    return confirm_url


class MyEmailBackend(EmailBackend):
  def _get_filename(self):
    self._fname = os.path.join(self.file_path, 'test_authn_user_flows.log')
    return self._fname
