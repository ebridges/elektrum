import os
import pytest
import functools

from base.tests.util import USER_PASSWORD, email_log


@pytest.fixture
def authenticated_client(client, user_factory):
    user = user_factory()
    client.get = functools.partial(client.get, secure=True)
    client.post = functools.partial(client.post, secure=True)
    login_result = client.login(email=user.email, password=USER_PASSWORD)

    assert login_result, 'Unable to login'
    return client, user


@pytest.fixture
def mock_email_log():
    yield email_log
    if os.path.exists(email_log):
        os.remove(email_log)
