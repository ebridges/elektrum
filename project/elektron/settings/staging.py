import requests

DEBUG = True
ALLOWED_HOSTS = ['elektron-staging.us-east-1.elasticbeanstalk.com', '127.0.0.1', 'localhost']

try:
    internal_ip = requests.get('http://instance-data/latest/meta-data/local-ipv4').text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)

del requests
