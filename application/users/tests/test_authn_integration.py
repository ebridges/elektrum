from urllib.parse import urlparse

from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from allauth.account.models import EmailAddress

from users.models import CustomUser

from base.tests.util import USER_PASSWORD
from users.tests.factories import UserFactory

import pytest

# pytestmark = pytest.mark.skip(reason="The app only supports Google Auth. This is left behind for legacy reasons.")
pytest.skip(
    reason="The app only supports Google Auth. This is left behind for legacy reasons.",
    allow_module_level=True,
)


def util_login_user(driver, live_server_url, user_email, password):
    u = urlparse(live_server_url)
    url = '%s://%s:%s/' % (u.scheme, u.hostname, u.port)
    driver.get(url)
    username_input = driver.find_element(By.NAME, 'login')
    username_input.send_keys(user_email)
    password_input = driver.find_element(By.NAME, 'password')
    password_input.send_keys(password)
    driver.find_element_by_xpath('//button').click()


@override_settings(SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class AuthnIntegrationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(5)
        except WebDriverException as e:
            print(f"WebDriverException: {e}")
            raise

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
