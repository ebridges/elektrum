import pytest

from django.test.utils import override_settings
from allauth.account.models import EmailAddress

from base.tests import util
from users.tests.factories import USER_PASSWORD
from users.models import CustomUser


@pytest.mark.django_db
def test_login_failure(client, user_factory):
    """
    Test failed login
    :param client: mock django client
    :param user_factory: mock user generator
    :return:
    """
    u = user_factory()
    result = client.login(email=u.email, password='wrong_password')
    assert not result, 'Should not be able to login with wrong password'


@pytest.mark.django_db
def test_login_via_post(client, user_factory):
    """
    Test successful login via POST
    :param client: mock django client
    :param user_factory: mock user generator
    """
    u = user_factory()
    response = client.post('/account/login/', {'login': u.email, 'password': USER_PASSWORD})
    util.assert_account_redirects(response)
    user = CustomUser.objects.get(username=u.username)
    assert user is not None, 'could not locate user with username %s' % u.username
    assert response.context['user'].email == user.email
    assert user.email == u.email


@pytest.mark.django_db
def test_csrf_login_failure(client, user_factory):
    """
    Test login failed via POST when enforcing csrf
    :param client: mock django client
    :param user_factory: mock user generator
    """
    u = user_factory()
    client.handler.enforce_csrf_checks=True
    response = client.post('/account/login/', {'login': u.email, 'password': USER_PASSWORD})
    assert response.status_code == 403


@pytest.mark.django_db
def test_logout(authenticated_client):
    """
    Confirm successful logout
    :param authenticated_client: mock django client that has been logged in
    """
    (c, __) = authenticated_client
    response = c.post('/account/logout/')
    util.assert_account_redirects(response, expected_url='/')


@pytest.mark.django_db
def test_csrf_logout_failure(authenticated_client):
    """
    Confirm failed logout when CSRF is enforced
    :param authenticated_client: mock django client that has been logged in
    """
    (c, __) = authenticated_client
    c.handler.enforce_csrf_checks=True
    response = c.post('/account/logout/')
    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='users.tests.factories.MyEmailBackend')
# https://stackoverflow.com/a/15053970/87408
def test_signup_flow(client, mock_email_log):
    """
    Confirm signup flow and email verification.
    :param client: mock django client
    :param mock_email_log: file where verification email gets written.
    """
    expected_email = 'newuser@example.com'
    expected_username = 'newuser'
    response = client.post('/account/signup/',
                  {'email': expected_email, 'username': expected_username, 'first_name': 'first',
                   'last_name': 'last', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    util.assert_account_redirects(response)
    confirm_url = util.assert_signup_mail(expected_email, mock_email_log)
    assert confirm_url is not None
    confirm_response = client.post(confirm_url)

    # Because `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION` is "True", the user is redirected to '/'
    # If there is some delay (see docs on that setting) then the redirect will be to '/account/login/'
    util.assert_account_redirects(confirm_response, expected_url='/app-home')

    email = EmailAddress.objects.get(email=expected_email)
    assert email.verified

    user = CustomUser.objects.get(username=expected_username)
    assert user.is_account_verified()


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='users.tests.factories.MyEmailBackend')
def test_signup_flow_multiple(client, mock_email_log):
    """
    Confirm signup flow and email verification.
    :param client: mock django client
    :param mock_email_log: file where verification email gets written.
    """
    response = client.post('/account/signup/',
                      {'username': 'newuser2', 'email': 'newuser2@example.com', 'first_name': 'first2',
                       'last_name': 'last2', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    util.assert_account_redirects(response)
    util.assert_signup_mail('newuser2@example.com', mock_email_log)

    util.trunc_file(mock_email_log)

    response = client.post('/account/signup/',
                      {'username': 'newuser3', 'email': 'newuser3@example.com', 'first_name': 'first3',
                       'last_name': 'last3', 'password1': 'abcd@1234', 'password2': 'abcd@1234'})
    util.assert_account_redirects(response)
    util.assert_signup_mail('newuser3@example.com', mock_email_log)
