import json

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from allauth.account.models import EmailAddress

from users.models import CustomUser

from base.tests.util import USER_PASSWORD, util_login_user
from users.tests.factories import UserFactory


class AuthnIntegrationTests(StaticLiveServerTestCase):

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

    def test_login_with_verification(self):
        u = UserFactory()
        user = CustomUser.objects.get(username=u.username)
        email = EmailAddress.objects.add_email(request=None, user=user, email=user.email)
        email.verified = True
        email.save()

        util_login_user(self.driver, self.live_server_url, user.email, USER_PASSWORD)
        self.assertInHTML('<a href="/account/logout/">Logout</a>', self.driver.page_source, count=1)

    # def test_login_without_verification(self):
    #     u = UserFactory()
    #     user = CustomUser.objects.get(username=u.username)
    #     email = EmailAddress.objects.add_email(request=None, user=user, email=user.email)
    #     email.verified = False
    #     email.save()
    #
    #     util_login_user(self.driver, self.live_server_url, u.email, USER_PASSWORD)
    #     self.assertInHTML('Verify Your E-mail Address', self.driver.page_source)
