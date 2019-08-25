"""
Django settings for elektron project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
from elektron.env_util import locate_env_file, resolve_version
import dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_file = locate_env_file(BASE_DIR)
dotenv.read_dotenv(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('django_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('django_debug_enabled') else False

allowed_hosts = os.getenv('django_allowed_hosts')
ALLOWED_HOSTS = allowed_hosts.split(',')

# establish project root directory as a variable
ELEKTRON_PROJECT_DIR = os.path.abspath('%s/..' % BASE_DIR)

# read version number for display in the app
version_file = resolve_version(BASE_DIR)
if os.path.isfile(version_file):
    with open(version_file) as v_file:
        APP_VERSION_NUMBER = v_file.read()
print('Running Elektron v%s' % APP_VERSION_NUMBER)

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
    'sslserver',
    'meta',
    'base',
    'users',
    'pages',
    'media_items',
    'date_dimension',
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

ROOT_URLCONF = 'elektron.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'pages/templates'),
            os.path.join(BASE_DIR, 'users/templates'),
            os.path.join(BASE_DIR, 'media_items/templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'elektron.context_processors.selected_settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'elektron.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        # See issue #45
        # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('db_name'),
        'USER': os.getenv('db_username'),
        'PASSWORD': os.getenv('db_password'),
        'HOST': os.getenv('db_hostname'),
        'PORT': os.getenv('db_port_num'),
    }
}

# substring search across cmdline args
if [s for s in sys.argv if 'pytest' in s]:
    DATABASES['default'] = {
        # see #14 - SQLite backend is not working for some tests
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'test-db.sqlite3'),
        #
        # see issue #45
        # 'ENGINE': 'django.contrib.gis.db.backends.postgis',

        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "media_info",
        'USER': "ebridges",
        'PASSWORD': "ebridges",
        'HOST': "localhost",
        'PORT': 5432,
    }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.getenv('static_files_bucket_name')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('static_domain_name')
STATIC_URL = 'https//%s/' % AWS_S3_CUSTOM_DOMAIN
AWS_DEFAULT_ACL = "public-read"

LOGIN_URL = '/account/login/'  # is there a better way to do this?
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_ADAPTER = 'elektron.urls.ElektronAccountAdapter'
LOGOUT_REDIRECT_URL = 'home'
AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomUserCreationForm',
}

SITE_ID = 2

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
EMAIL_BACKEND = os.getenv('django_email_backend')
EMAIL_FILE_PATH = './sent_emails'

TEST_RUNNER = 'elektron.test_runner.PytestTestRunner'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] [{asctime}] [{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'elektron': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
