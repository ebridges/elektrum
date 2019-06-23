from .base import *
import os
import requests

DEBUG = False
ALLOWED_HOSTS = ['elektron.photos']
SECRET_KEY = os.getenv('secret_key')

try:
    internal_ip = requests.get('http://instance-data/latest/meta-data/local-ipv4').text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)

del requests
