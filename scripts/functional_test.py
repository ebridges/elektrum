#!/usr/bin/env python

import argparse
from logging import INFO, DEBUG, CRITICAL, basicConfig, info, debug, error, disable, getLogger
import subprocess
import os
import sys
import signal
from pathlib import PurePath
from threading import Thread
import time
import records
import requests
import uuid
from urllib.parse import urlparse
from dotenv import load_dotenv
from django import setup
from django.contrib.auth.hashers import make_password
from boto3 import Session, resource, client

CREATE_DATE = '2020-01-01T10:10:10'
TEST_IMAGE = 'scripts/resources/test-file-upload.jpg'
TEST_BUCKET_NAME = 'com.example.functionaltest'

processes = []
threads = []
success = True


def main(args):
    initialize_environment()
    user = None
    try:
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

        response = upload_image(client,
                                request.headers.get('Location'),
                                request.headers.get('X-Elektron-Filename')
                                )
        assert_upload(response)

    finally:
        teardown_bucket()
        if user:
            teardown_media_item(user['username'])
            teardown_user(user['id'])
        terminate()

    if success:
        print('Functional Test: \033[32m[OK]\033[m')
        return 0
    else:
        print('Functional Test: \033[31m[NOT OK]\033[m')
        return 1


def assert_upload(response):
    assert_equals('Status Code', 200, response.status_code)
    request_url = urlparse(response.request.url)
    bucket, key = split_path(request_url.path)

    actual_size = get_object_size(bucket, key)
    assert_not_none('Actual image size', actual_size)

    expected_size = response.request.headers['content-length']
    assert_not_none('Expected image size', expected_size)

    assert_equals('uploaded image size', int(expected_size), actual_size)


def split_path(path):
    p = PurePath(path.strip('/'))
    bucket = p.parts[0]
    key = os.path.join('/', *p.parts[1:]).strip('/')
    return bucket, key


def get_object_size(bucket, key):
    """return the key's size if it exist, else None"""
    s3 = resource('s3')
    bucket = s3.Bucket(bucket)

    for o in bucket.objects.all():
        if key == o.key:
            return o.size


def upload_image(client, url, filename):
    debug('Uploading image [%s] to [%s]' % (filename, url))
    files = {
        'file': (filename, open(TEST_IMAGE, 'rb'), 'image/jpeg')
    }
    response = client.put(url, files=files)
    info('Image uploaded [%s] to [%s]' % (filename, url))
    return response


def assert_upload_request(request):
    assert_equals('Status Code', 201, request.status_code)
    assert_not_none('Location', request.headers.get('Location'))
    assert_not_none('X-Elektron-Media-Id', request.headers.get('X-Elektron-Media-Id'))
    media_item_id = request.headers.get('X-Elektron-Media-Id')
    assert_not_none('X-Elektron-Filename', request.headers.get('X-Elektron-Filename'))
    assert_not_none('Media Item', query_media_item(media_item_id))


def teardown_bucket():
    debug('Deleting test bucket [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    access_secret = os.environ['AWS_SECRET_ACCESS_KEY']
    bucket_name = os.environ['AWS_UPLOAD_BUCKET_NAME']
    s3 = resource('s3', aws_access_key_id=access_key,
                  aws_secret_access_key=access_secret)
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()
    info('Deleted test bucket: [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])


def setup_bucket():
    debug('Creating test bucket [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    access_secret = os.environ['AWS_SECRET_ACCESS_KEY']
    bucket_name = os.environ['AWS_UPLOAD_BUCKET_NAME']
    session = Session(aws_access_key_id=access_key, aws_secret_access_key=access_secret)
    s3client = session.client('s3')
    s3client.create_bucket(Bucket=bucket_name)
    info('Created test bucket: [%s]' % os.environ['AWS_UPLOAD_BUCKET_NAME'])


def upload_request(client):
    debug('Initializing an upload request.')
    url = 'http://localhost:8000/media/request-upload/'
    payload = {
        'create_date': CREATE_DATE,
        'mime_type': 'image/jpeg'
    }
    headers = get_csrf_headers(client)
    r = client.post(url, data=payload, headers=headers)
    info('Initialized upload request.')
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
    info('Client authenticated: [%s]' % user['email'])
    return client


def get_csrf_headers(client):
    csrftoken = client.cookies.get('csrftoken')
    return {
        'X-CSRFToken': csrftoken
    }


def setup_django():
    debug('Initializing Django settings.')
    setup()
    info('Initialized Django settings.')


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
    """ % (user['id'], user['username'], encoded_password, user['email'], user['first_name'], user['last_name']))

    db.query("""
        insert into account_emailaddress
        (email, verified, "primary", user_id)
        values ('%s', 'true', 'true', '%s')
    """ % (user['email'], user['id']))

    info('Created test user: [%s]' % user['id'])
    return user


def query_media_item(id):
    if not id:
        return None
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
    info('Deleted test user: [%s]' % id)


def teardown_media_item(username):
    debug('Deleting test media item for user [%s]' % username)
    db_url = connect_info()
    db = records.Database(db_url)
    db.query(
        "delete from media_item where owner_id = (select id from users_customuser where username = '%s')" % username)
    info('Deleted media item for user: [%s]' % username)


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
            info('Stopped: [%s]' % thread.name)

    info('Test infrastructure stopped.')


def http_server():
    global processes
    info('Starting Django server process')
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


def configure_logging(level=None):
    if not level:
        level = DEBUG

    if level == sys.maxsize:
        disable(sys.maxsize)

    if level == 'VERBOSE':
        getLogger('botocore').setLevel(DEBUG)
        getLogger('boto3').setLevel(DEBUG)
        level = DEBUG
    else:
        getLogger('botocore').setLevel(CRITICAL)
        getLogger('boto3').setLevel(CRITICAL)

    basicConfig(
        format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        level=level)


def initialize_environment():
    # Elektron env
    os.environ['ELEKTRON_ENV'] = 'development'
    load_dotenv('etc/env/%s.env' % os.environ['ELEKTRON_ENV'])

    # Django env
    sys.path.append('/Users/ebridges/Documents/elektron-working/elektron/project')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'elektron.settings'

    # AWS_SECRET_ACCESS_KEY & AWS_ACCESS_KEY_ID assumed in runtime env
    os.environ['AWS_UPLOAD_BUCKET_NAME'] = TEST_BUCKET_NAME


def assert_equals(name, expected, actual):
    global success
    try:
        assert expected == actual
    except AssertionError:
        print('\033[31m[ERROR] Expected %s for %s but got %s\033[m' % (expected, name, actual))
        error('Expected %s for %s but got %s' % (expected, name, actual))
        success = False


def assert_not_none(name, value):
    global success
    try:
        assert value is not None
    except AssertionError:
        print('\033[31m[ERROR] %s is None\033[m' % name)
        error('[%s] is None' % name)
        success = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-http-server', action='store_true', required=False, default=False,
                        help='Disable Django server.')
    parser.add_argument('--level', nargs='?', choices=['INFO', 'DEBUG', 'VERBOSE'], required=False, default=sys.maxsize,
                        help='Log level. Default is "off"')
    args = parser.parse_args()
    configure_logging(args.level)
    main(args)
