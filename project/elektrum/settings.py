"""
Django settings for elektrum project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
from elektrum.env_util import locate_env_file, resolve_version
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_file = locate_env_file(BASE_DIR)
load_dotenv(env_file)
OPERATING_ENV = os.environ['ENVIRONMENT']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if 'DJANGO_DEBUG_ENABLED' in os.environ else False

allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts.split(',')

# read version number for display in the app
version_file = resolve_version(BASE_DIR)
if os.path.isfile(version_file):
    with open(version_file) as v_file:
        v = v_file.read()
        APP_VERSION_NUMBER = v.strip()
print('Running Elektrum (%s) v%s' % (OPERATING_ENV, APP_VERSION_NUMBER))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'django.contrib.sites',
    #    'django.contrib.gis',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework.authtoken',
    'sslserver',
    'meta',
    'base',
    'users',
    'pages',
    'media_items',
    'date_dimension',
    'sharing',
    'request_id',
]

if os.environ.get('OPERATING_ENV') == 'local':
    INSTALLED_APPS.append('django_extensions')


MIDDLEWARE = [
    'request_id.middleware.RequestIdMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

ROOT_URLCONF = 'elektrum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'pages/templates'),
            os.path.join(BASE_DIR, 'users/templates'),
            os.path.join(BASE_DIR, 'media_items/templates'),
            os.path.join(BASE_DIR, 'sharing/templates'),
            os.path.join(BASE_DIR, 'emailer/templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'elektrum.context_processors.selected_settings',
            ]
        },
    }
]

WSGI_APPLICATION = 'elektrum.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


if [s for s in sys.argv if 'test' in s]:
    IN_TEST_MODE = True
else:
    IN_TEST_MODE = False

if IN_TEST_MODE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'TEST': {'NAME': os.path.join(BASE_DIR, 'test-db.sqlite3')},
        }
    }
else:
    DATABASES = {
        'default': {
            # See issue #45
            # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USERNAME'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOSTNAME'),
            'PORT': os.getenv('DB_PORT_NUM'),
        }
    }
CONN_MAX_AGE = 60

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.getenv('STATIC_FILES_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('STATIC_DOMAIN_NAME')
STATIC_URL = 'https//%s/' % AWS_S3_CUSTOM_DOMAIN
AWS_DEFAULT_ACL = 'public-read'

LOGIN_URL = '/account/login/'  # is there a better way to do this?
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_ADAPTER = 'elektrum.urls.ElektrumAccountAdapter'
LOGOUT_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_FORMS = {'signup': 'users.forms.CustomUserCreationForm'}

SITE_ID = 2

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['base.authentication.BearerTokenAuthentication']
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ADMINS = [(os.getenv('ADMIN_CONTACT_NAME'), os.getenv('ADMIN_CONTACT_EMAIL'))]
EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND')
EMAIL_FILE_PATH = './sent_emails'
DEFAULT_FROM_EMAIL = 'postmaster@%s' % os.getenv('APPLICATION_DOMAIN_NAME')
SERVER_EMAIL = 'admin@%s' % os.getenv('APPLICATION_DOMAIN_NAME')

SOCIALACCOUNT_PROVIDERS = {
    'google': {'SCOPE': ['profile', 'email'], 'AUTH_PARAMS': {'access_type': 'online'}}
}

TEST_RUNNER = 'elektrum.test_runner.PytestTestRunner'

DJANGO_LOGGING_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {'request_id': {'()': 'request_id.logging.RequestIdFilter'}},
    'formatters': {
        'verbose': {
            'format': '[{levelname}] [{request_id}] [{name}] [{asctime}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'filters': ['request_id'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        }
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        'elektrum': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django': {'handlers': ['console'], 'level': DJANGO_LOGGING_LEVEL, 'propagate': False},
        'django.utils.autoreload': {'handlers': ['console'], 'level': 'WARNING'},
        'selenium.webdriver.remote.remote_connection': {'handlers': ['console'], 'level': 'INFO'},
        'urllib3.connectionpool': {'handlers': ['console'], 'level': 'INFO'},
        '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = ['origin-when-cross-origin', 'same-origin', 'strict-origin', 'origin']
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

REQUEST_ID_HEADER = None

sentry_sdk.init(
    dsn='https://80cf5293784d494c97184d00979fa4b2@o397351.ingest.sentry.io/5251733',
    integrations=[DjangoIntegration()],
    release=f'{APP_VERSION_NUMBER}',
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=False,
    traces_sample_rate=0.50,
    environment=OPERATING_ENV,
    _experiments={'auto_enabling_integrations': True},
)
