from .base import *
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = './sent_emails'
TEST_RUNNER = 'elektron.test_runner.PytestTestRunner'
