import json
from urllib.parse import urlparse

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from allauth.account.models import EmailAddress

from users.models import CustomUser

from base.tests.util import USER_PASSWORD
from users.tests.factories import UserFactory


def util_login_user(driver, live_server_url, user_email, password):
    u = urlparse(live_server_url)
    url = '%s://%s:%s/' % (u.scheme, u.hostname, u.port)
    driver.get(url)
    username_input = driver.find_element_by_name('login')
    username_input.send_keys(user_email)
    password_input = driver.find_element_by_name('password')
    password_input.send_keys(password)
    driver.find_element_by_xpath('//button').click()


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class AuthnIntegrationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login_with_verification(self):
        u = UserFactory()
        user = CustomUser.objects.get(username=u.username)
        email = EmailAddress.objects.add_email(request=None, user=user, email=user.email)
        email.verified = True
        email.save()

        util_login_user(self.driver, self.live_server_url, user.email, USER_PASSWORD)
        self.assertInHTML('<a href="/account/logout/">Logout</a>', self.driver.page_source, count=1)
