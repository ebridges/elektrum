from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = [ 'elektron-production.us-east-1.elasticbeanstalk.com', '127.0.0.1', 'localhost'  ]
SECRET_KEY=os.getenv('secret_key')

import requests
try:
    internal_ip = requests.get('http://instance-data/latest/meta-data/local-ipv4').text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)
del requests