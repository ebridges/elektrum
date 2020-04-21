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

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_file = locate_env_file(BASE_DIR)
load_dotenv(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('DJANGO_DEBUG_ENABLED') else False

allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts.split(',')

# read version number for display in the app
version_file = resolve_version(BASE_DIR)
if os.path.isfile(version_file):
    with open(version_file) as v_file:
        v = v_file.read()
        APP_VERSION_NUMBER = v.strip()
print('Running Elektrum v%s' % APP_VERSION_NUMBER)

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
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND')
EMAIL_FILE_PATH = './sent_emails'

TEST_RUNNER = 'elektrum.test_runner.PytestTestRunner'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {'format': '[{levelname}] [{asctime}] [{name}] {message}', 'style': '{'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose', 'level': 'DEBUG'}
    },
    'loggers': {
        'elektrum': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.utils.autoreload': {'handlers': ['console'], 'level': 'WARNING'},
        'selenium.webdriver.remote.remote_connection': {'handlers': ['console'], 'level': 'INFO'},
        'urllib3.connectionpool': {'handlers': ['console'], 'level': 'INFO'},
        '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
