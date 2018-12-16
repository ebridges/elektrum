from django.test import TestCase
from django.test import Client
from .models import CustomUser

# Create your tests here.
class SimpleTest(TestCase):
  def setUp(self):
    user = CustomUser.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

  def test_login(self):
    c = Client()
    result = c.login(email='temporary@gmail.com', password='temporary')
    self.assertTrue(result)

  def test_login_fail(self):
    c = Client()
    result = c.login(email='temporary@gmail.com', password='xxxxxx')
    self.assertFalse(result)

  def test_login_via_post(self):
    c = Client()
    response = c.post('/account/login/', {'login': 'temporary@gmail.com', 'password': 'temporary'})
    self.assertRedirects(response, '/', status_code=302)
    user = CustomUser.objects.get(username='temporary')
    self.assertEqual(response.context['user'].email, user.email)

  def test_csrf_login_failure(self):
    c = Client(enforce_csrf_checks=True)
    response = c.post('/account/login/', {'login': 'temporary@gmail.com', 'password': 'temporary'})
    self.assertEqual(response.status_code, 403)

  def test_logout(self):
    c = Client()
    result = c.login(email='temporary@gmail.com', password='temporary')
    self.assertTrue(result)
    response = c.post('/account/logout/')
    self.assertRedirects(response, '/', status_code=302)

  def test_csrf_logout_failure(self):
    c = Client(enforce_csrf_checks=True)
    response = c.post('/account/logout/')
    self.assertEqual(response.status_code, 403)
