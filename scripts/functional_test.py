#!/usr/bin/env python

import argparse
from logging import INFO, DEBUG, basicConfig, info, debug, error, disable, getLogger
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
from boto3 import Session, resource

processes = []
threads = []

def main(args):
  initialize_environment()
  user = None
  try:
    initiate('localstack', localstack)
    if not args.no_http_server:
      initiate('http_server', http_server)

    setup_bucket()
    setup_django()
    user = setup_user()
    if not user:
      raise ValueError('no user created')
    
    client = authenticated_client(user)
    request = upload_request(client)
    assert_upload_request(request)
  finally:
    teardown_bucket()
    if user:
      teardown_media_item(user['id'])
      teardown_user(user['id'])
    terminate()
  
  print('Functional Test: \033[32m[OK]\033[m')
  return 0


def assert_upload_request(request):
  assertNotNone('Location', request.headers.get('Location'))
  assertNotNone('X-Elektron-Media-Id', request.headers.get('X-Elektron-Media-Id'))
  media_item_id = request.headers.get('X-Elektron-Media-Id')
  assertNotNone('Media Item', query_media_item(media_item_id))


def teardown_bucket():
  debug('Deleting test bucket [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])
  access_key = os.environ['AWS_ACCESS_KEY_ID']
  access_secret = os.environ['AWS_SECRET_ACCESS_KEY']
  endpoint_url = os.environ['AWS_S3_ENDPOINT_URL']
  bucket_name = os.environ['AWS_UPLOAD_BUCKET_NAME']
  s3 = resource('s3', aws_access_key_id=access_key, 
    aws_secret_access_key=access_secret, 
    endpoint_url=endpoint_url)
  bucket = s3.Bucket(bucket_name)
  bucket.objects.all().delete()
  bucket.delete()
  info('Test bucket deleted [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])


def setup_bucket():
  debug('Creating test bucket [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])
  access_key = os.environ['AWS_ACCESS_KEY_ID']
  access_secret = os.environ['AWS_SECRET_ACCESS_KEY']
  endpoint_url = os.environ['AWS_S3_ENDPOINT_URL']
  bucket_name = os.environ['AWS_UPLOAD_BUCKET_NAME']
  session = Session(aws_access_key_id=access_key, aws_secret_access_key=access_secret)
  s3client = session.client('s3', endpoint_url=endpoint_url)
  s3client.create_bucket(Bucket=bucket_name)
  info('Test bucket created [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])


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


def query_media_item(id):
  debug('Querying for media_item [%s]' % id)
  db_url = connect_info()
  db = records.Database(db_url)
  rows = db.query("select id from media_item where id = '%s'" % id)
  return rows.first()


def teardown_user(id):
  debug('Deleting test user [%s]' % id)
  db_url = connect_info()
  db = records.Database(db_url)
  db.query("delete from account_emailaddress where user_id = '%s'" % id)
  db.query("delete from users_customuser where id = '%s'" % id)
  info('Test user deleted.')


def teardown_media_item(id):
  debug('Deleting test media item for user [%s]' % id)
  db_url = connect_info()
  db = records.Database(db_url)
  db.query("delete from media_item where owner_id = '%s'" % id)
  info('Test media item deleted.')


def connect_info():
  return 'postgresql://%s:%s@%s:%s/%s' % (
    os.getenv('db_username'), 
    os.getenv('db_password'),
    os.getenv('db_hostname'),
    os.getenv('db_port_num'),
    os.getenv('db_name'))


def initiate(name, target):
  debug('Initiating [%s] thread.', name)
  global threads
  s = Thread(name=name, target=target)
  s.start()
  time.sleep(5)
  info('Started: [%s]' % name)
  threads.append(s)
  return s


def terminate():
  debug('Shutting down processes for test infrastructure.')
  for process in processes:
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
  global processes
  http_server_process = subprocess.Popen(
    args='python3 manage.py runserver', 
    stdout=subprocess.DEVNULL,
    shell=True,
    preexec_fn=os.setsid,
    cwd='./project',
    stderr=subprocess.DEVNULL
  )
  processes.append(http_server_process)
  debug('> Django server process: [%s]' % http_server_process.pid)


def localstack():
  global processes
  localstack_process = subprocess.Popen(
    args='docker-compose --file scripts/localstack-compose.yml up', 
    stdout=subprocess.DEVNULL,
    shell=True,
    preexec_fn=os.setsid,
    stderr=subprocess.DEVNULL
  )
  processes.append(localstack_process)
  debug('> Mock AWS server process: [%s]' % localstack_process.pid)


def configure_logging(level=None):
  if not level:
    level = DEBUG
  if level == sys.maxsize:
    disable(sys.maxsize)
  basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    level=level)
  

def initialize_environment():
  ## Elektron env
  os.environ['ELEKTRON_ENV'] = 'development'
  load_dotenv('etc/env/%s.env' % os.environ['ELEKTRON_ENV'])

  ## Django env
  sys.path.append('/Users/ebridges/Documents/elektron-working/elektron/project')
  os.environ['DJANGO_SETTINGS_MODULE'] = 'elektron.settings'

  ## Localstack env
  ### AWS_SECRET_ACCESS_KEY & AWS_ACCESS_KEY_ID assumed in runtime env
  os.environ['SERVICES'] = 's3,lambda'
  os.environ['TMPDIR'] = '/private%s' % os.environ['TMPDIR']
  os.environ['AWS_UPLOAD_BUCKET_NAME'] = 'com.example.functional_test'
  os.environ['AWS_S3_ENDPOINT_URL'] = 'http://localhost:4572'


def assertNotNone(name, value):
  try:
    assert value is not None
  except AssertionError:
    print('Functional Test: \033[31m[ERROR] %s is None\033[m' % name)
    error('[%s] is None' % name)
    try:
      sys.exit(1)
    except SystemExit:
      raise


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--no-http-server', action='store_false', required=False, default=False, help='Disable Django server.')
  parser.add_argument('--level', nargs='?', choices=['INFO', 'DEBUG'], required=False, default=sys.maxsize, help='Log level. Default is "off"')
  args = parser.parse_args()
  configure_logging(args.level)
  main(args)
