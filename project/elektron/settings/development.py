from .base import *
DEBUG = True
ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = './sent_emails'
TEST_RUNNER = 'elektron.test_runner.PytestTestRunner'
