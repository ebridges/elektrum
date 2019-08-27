#!/usr/bin/env python
import os

import django
import logging_tree

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elektrum.settings')

SECRET_KEY = 'not-secret'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

if __name__ == '__main__':
    django.setup()
    logging_tree.printout()
