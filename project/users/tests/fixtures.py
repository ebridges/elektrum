import os
import pytest

from users.tests.factories import USER_PASSWORD, email_log


@pytest.fixture
def authenticated_client(client, user_factory):
    u = user_factory()
    login_result = client.login(email=u.email,
                                password=USER_PASSWORD)
    assert login_result, 'Unable to login'
    return client


@pytest.fixture
def mock_email_log():
    yield email_log
    if os.path.exists(email_log):
        os.remove(email_log)
