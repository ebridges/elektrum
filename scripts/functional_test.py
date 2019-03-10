#!/usr/bin/env python

from logging import INFO, DEBUG, basicConfig, info, debug, error
import subprocess
import os
import sys
import signal
from threading import Thread
import time
import records
import requests
import uuid
from dotenv import load_dotenv
from django import setup
from django.contrib.auth.hashers import make_password

# start up local django server


# start up localstack

# invoke call to get a presigned upload URL

# upload image to bucket

# assert upload succeeded

# assert metadata properly recorded\

def main():
  initialize_environment()  
  try:
    localstack_thread = initiate('localstack', localstack)
    http_server_thread = initiate('http_server', http_server)

    setup_django()
    user = setup_user()
    if not user:
      raise ValueError('no user created')
    
    client = authenticated_client(user)
    request = upload_request(client)
    assert_upload_request(request)
    return 1
  finally:
    if user:
      teardown_user(user['id'])
      terminate([http_server_thread])


def assert_upload_request(request):
  assertNotNone('Location', request.headers.get('Location'))
  assertNotNone('X-Elektron-Media-Id', request.headers.get('X-Elektron-Media-Id'))


def upload_request(client):
  debug('Initializing an upload request.')
  url = 'http://localhost:8000/media/request-upload/'
  payload = { 
    'create_date': '2020-01-01T10:10:10',
    'mime_type': 'image/jpeg'
  }
  headers = get_csrf_headers(client)
  r = client.post(url, data=payload, headers=headers)
  info('Upload request initialized.')
  return r

def authenticated_client(user):
  debug('Creating an authenticated client.')
  client = requests.session()
  r = client.get('http://localhost:8000/')
  url = 'http://localhost:8000/account/login/'
  payload = {
    'login': user['email'],
    'password': user['password']
  }
  headers = get_csrf_headers(client)
  client.post(url, data=payload, headers=headers)
  info('Client authenticated.')
  return client


def get_csrf_headers(client):
  csrftoken = client.cookies.get('csrftoken')
  return {
    'X-CSRFToken': csrftoken
  }


def setup_django():
  debug('Initializing Django settings.')
  setup()
  info('Django settings initialized.')


def setup_user():
  db_url = connect_info()
  db = records.Database(db_url)

  user = {
    'id': uuid.uuid4(),
    'username': 'abcdefg_username',
    'password': 'abcdefg_password',
    'first_name': 'abcdefg_fname',
    'last_name': 'abcdefg_lname',
    'email': 'abcdefg@example.com'
  }

  encoded_password = make_password(user['password'])

  debug('Creating test user [%s]' % user['id'])
  db.query("""
    insert into users_customuser 
    (id, username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined)
    values ('%s', '%s', '%s', '%s', '%s', '%s', 'false', 'false', 'true', '2020-01-01 10:10:10')
    """ %  (user['id'], user['username'], encoded_password, user['email'], user['first_name'], user['last_name']))
  db.query("""
  insert into account_emailaddress
  (email, verified, "primary", user_id)
  values ('%s', 'true', 'true', '%s')
  """ % (user['email'], user['id']))

  info('Test user created [%s]' % user['id'])
  return user


def teardown_user(id):
  debug('Deleting test user [%s]' % id)
  db_url = connect_info()
  db = records.Database(db_url)
  db.query("delete from account_emailaddress where user_id = '%s'" % id)
  db.query("delete from users_customuser where id = '%s'" % id)
  info('Test user deleted.')


def connect_info():
  return 'postgresql://%s:%s@%s:%s/%s' % (
    os.getenv('db_username'), 
    os.getenv('db_password'),
    os.getenv('db_hostname'),
    os.getenv('db_port_num'),
    os.getenv('db_name'))


def initiate(name, target):
  debug('Initiating [%s] thread.', name)
  s = Thread(name=name, target=target)
  s.start()
  time.sleep(5)
  info('Started: [%s]' % name)
  return s


def terminate(threads):
  debug('Shutting down processes for test infrastructure.')
  # for process in [http_server_process, localstack_process]:
  for process in [http_server_process]:
    if process:
      debug('> Stopping process [%s]', process.pid)
      os.killpg(os.getpgid(process.pid), signal.SIGTERM)

  time.sleep(5)

  for thread in threads:
    if thread:
      debug('> Waiting on [%s] thread.' % thread.name)
      thread.join()

  info('Test infrastructure stopped.')


def http_server():
  global http_server_process
  http_server_process = subprocess.Popen(
    args='python3 manage.py runserver', 
    stdout=subprocess.PIPE,
    shell=True,
    preexec_fn=os.setsid,
    cwd='./project'
  )
  debug('> Django server process: [%s]' % http_server_process.pid)


def localstack():
  global localstack_process
  localstack_process = subprocess.Popen(
    args='docker-compose --file scripts/localstack-compose.yml up', 
    stdout=subprocess.PIPE,
    shell=True,
    preexec_fn=os.setsid
  )
  debug('> Mock AWS server process: [%s]' % localstack_process.pid)


def configure_logging(verbose):
    if verbose:
        level = DEBUG
    else:
        level = INFO
    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level)


def initialize_environment():
  ## Elektron env
  os.environ['ELEKTRON_ENV'] = 'development'
  load_dotenv('etc/env/%s.env' % os.environ['ELEKTRON_ENV'])
  os.environ['AWS_UPLOAD_BUCKET_NAME'] = 'com.example.functional_test'

  ## Django env
  sys.path.append('/Users/ebridges/Documents/elektron-working/elektron/project')
  os.environ['DJANGO_SETTINGS_MODULE'] = 'elektron.settings'

  ## Localstack env
  os.environ['SERVICES'] = 's3,lambda'
  os.environ['TMPDIR'] = '/private%s' % os.environ['TMPDIR']


def assertNotNone(name, value):
  if value is None:
    error('[%s] is None' % name)


if __name__ == "__main__":
  verbosity = os.getenv('VERBOSE', 'yes')
  configure_logging(verbosity)
  main()