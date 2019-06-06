import os
import requests

DEBUG = True
ALLOWED_HOSTS = ['.execute-api.us-east-1.amazonaws.com', '127.0.0.1', 'localhost']

STATIC_HOST = os.environ.get('application_cdn_host', '')
STATIC_URL = STATIC_HOST + '/static/'

try:
    internal_ip = requests.get('http://instance-data/latest/meta-data/local-ipv4').text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)

del requests
