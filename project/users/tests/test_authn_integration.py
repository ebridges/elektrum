import json

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver 
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from allauth.account.models import EmailAddress

from users.models import CustomUser

class AuthnIntegrationTests(StaticLiveServerTestCase):
  fixtures = ['users/tests/user-data.json']

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    cls.driver = webdriver.Chrome(chrome_options=chrome_options)
    cls.driver.implicitly_wait(10)

 
  @classmethod
  def tearDownClass(cls):
    cls.driver.quit()
    super().tearDownClass()


  def setUp(self):
    self.password='temporary'
    with open('users/tests/user-data.json') as f:
        d = json.load(f)
        self.data=d[0]

    user = CustomUser.objects.get(username=self.data['fields']['username'])
    email = EmailAddress.objects.add_email(request=None, user=user, email=self.data['fields']['email'])
    email.verified = True
    email.save()


  def test_login(self):
    self.driver.get('%s%s' % (self.live_server_url, '/account/login/'))
    username_input = self.driver.find_element_by_name('login')
    username_input.send_keys(self.data['fields']['email'])
    password_input = self.driver.find_element_by_name('password')
    password_input.send_keys(self.password)
    self.driver.find_element_by_xpath('//button').click()
    self.assertInHTML('<a href="/account/logout/">Log out</a>', self.driver.page_source, count=1)
