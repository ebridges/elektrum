from django.test import TestCase
from django.test import Client
from users.models import CustomUser
import json


class AuthnUserFlowTest(TestCase):
  fixtures = ['users/tests/user-data.json']

  def setUp(self):
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

  def test_signup_flow(self):
    c = Client()
    response = c.post('/account/signup/', {'email': 'newuser@example.com', 'first_name': 'first', 'last_name': 'last', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)

  def test_signup_flow_multiple(self):
    c = Client()
    response = c.post('/account/signup/', {'email': 'newuser2@example.com', 'first_name': 'first2', 'last_name': 'last2', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)
    response = c.post('/account/signup/', {'email': 'newuser3@example.com', 'first_name': 'first3', 'last_name': 'last3', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    self.util_assert_account_redirects(response)

  def util_assert_account_redirects(self, response, expected_url='/account/confirm-email/', expected_redirect_sc=302, expected_target_sc=200):
    self.assertRedirects(response, expected_url, expected_redirect_sc, expected_target_sc)
