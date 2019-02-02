import json

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
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
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.password = 'temporary'
        with open('users/tests/user-data.json') as f:
            d = json.load(f)
            self.data = d

    def test_login_with_verification(self):
        user = CustomUser.objects.get(username=self.data[0]['fields']['username'])
        email = EmailAddress.objects.add_email(request=None, user=user, email=self.data[0]['fields']['email'])
        email.verified = True
        email.save()

        self.util_login_user(self.password)
        self.assertInHTML('<a href="/account/logout/">Log out</a>', self.driver.page_source, count=1)

    def test_login_without_verification(self):
        self.util_login_user(self.password)
        self.assertInHTML('<h1>Verify Your E-mail Address</h1>', self.driver.page_source, count=1)

    def util_login_user(self, password):
        self.driver.get('%s%s' % (self.live_server_url, '/account/login/'))
        username_input = self.driver.find_element_by_name('login')
        username_input.send_keys(self.data[0]['fields']['email'])
        password_input = self.driver.find_element_by_name('password')
        password_input.send_keys(password)
        self.driver.find_element_by_xpath('//button').click()
