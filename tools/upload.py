from argparse import ArgumentParser
from datetime import datetime
from logging import basicConfig, DEBUG, INFO, debug, info, warning, error
from os.path import isfile, splitext
from pprint import pprint
from re import match, IGNORECASE
from uuid import uuid4
from sys import argv, exit
from time import sleep
from urllib.parse import urlparse
from requests import post, put, head

UUID = '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[89AB][0-9A-F]{3}-[0-9A-F]{12}'
EXT = '[a-z]{3,4}'
IMAGE_KEY_PATTERN = f'^(?P<uid>{UUID})/(?P<iid>{UUID}).(?P<ext>{EXT})$'

MIME_TYPES = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}

UPLOAD_ENDPOINT = 'https://elektrum.dev/media/api/upload-request/'
CONFIRM_ENDPOINT = 'https://elektrum.dev/media/api/confirm-upload'
LOG_ENDPOINT = 'https://elektrum.dev/status/api/processor-log/item'


def upload(token, uid, photo):
    debug(f'Uploading photo {photo}')
    ext = splitext(photo)[1][1:]
    mime_type = MIME_TYPES[ext]
    upload_url, key = upload_request(token, uid, mime_type, photo)

    info(f'Uploading {photo} to {key}')
    result = upload_photo(token, upload_url, key, photo, mime_type)

    if result != 'ok':
        error(f'Upload failed.')
        return None

    confirm(token, key, photo)


def confirm(token, key, photo=None):
    confirm_url = f'{CONFIRM_ENDPOINT}/{key}'
    headers = {'Authorization': f'Bearer {token}'}
    chk_cnt = 0
    MAX_WAIT_SECS = 60
    sleep(2)
    while True:
        chk_cnt = chk_cnt + 1
        response = head(confirm_url, headers=headers)
        if response.status_code == 200:
            info(f'Image uploaded to {key} has completed processing.')
            break
        elif response.status_code == 403:
            if photo:
                log_error(
                    token,
                    key,
                    f'authorization error [{response.status_code}]',
                    'Authorization failure.',
                    reason=response.text,
                    file_path=photo,
                )
            error('Unauthorized.')
            break
        elif chk_cnt > MAX_WAIT_SECS:
            if photo:
                log_error(
                    token,
                    key,
                    f'processing-failed',
                    f'Image not completed processing after {MAX_WAIT_SECS} secs.',
                    file_path=photo,
                )
            warning(f'{key} has not completed processing after one minute, exiting.')
            break
        else:
            info(f'Image still pending processing.')
            sleep(1)


def upload_photo(token, upload_url, key, photo, mime_type):
    headers = {
        'Content-Type': mime_type,
        'Slug': key,
    }

    with open(photo, 'rb') as file_handle:
        response = put(upload_url, data=file_handle, headers=headers)

    if response.status_code == 200:
        info(f'Image uploaded under key {key}')
        return 'ok'
    else:
        log_error(
            token,
            key,
            f'upload-error [{response.status_code}]',
            f'Unable to upload photo',
            reason=response.text,
            file_path=photo,
        )
        error(f'Unable to upload [{photo}] under [{key}]: {response.text}')


def upload_request(token, uid, mime_type, photo):
    headers = {'Authorization': f'Bearer {token}'}
    body = {
        'mime_type': mime_type,
    }
    response = post(UPLOAD_ENDPOINT, data=body, headers=headers)
    if response.status_code == 201:
        upload_url = response.headers['location']
        if upload_url is None:
            raise Exception('Upload URL is empty.')
        u = urlparse(upload_url)
        key = u.path[1:]
        if key is None:
            raise Exception(f'Key is empty from url: {upload_url}')
        return upload_url, key
    else:
        log_error(
            token,
            uid,
            f'upload-error [{response.status_code}]',
            f'Unable to upload photo',
            reason=response.text,
            file_path=photo,
        )
        raise Exception(
            f'Unable to request upload photo url: [{response.status_code}] Error: {response.text}'
        )


def delete(token, uid, key):
    debug(f'Deleting photo {key}')
    raise NotImplementedError()


def log_error(token, owner_id, error_code, message, key=None, reason=None, file_path=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json',
    }

    event_date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    body = {
        'owner': owner_id,
        'event_date': event_date,
        'file_path': key,
        'error_code': error_code,
        'message': message,
        'reason': reason,
        'original_file_path': file_path,
    }

    response = post(LOG_ENDPOINT, headers=headers, data=body)
    if response.status_code != 201:
        raise Exception(
            f'Unable to log error: [{response.status_code }]: {response.text}.  Event: {body}'
        )


def parse(path):
    m = match(IMAGE_KEY_PATTERN, path, IGNORECASE)
    if m:
        uid = m.group('uid')
        iid = m.group('iid')
        ext = m.group('ext')
        return uid, iid, ext
    else:
        raise ValueError(f'image key in unexpected format: {path}')


def configure_logging(verbose):
    if verbose:
        level = DEBUG
    else:
        level = INFO

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=level
    )


if __name__ == '__main__':
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('-t', '--token', required=True, help='Auth token.')
    sp = parser.add_subparsers(
        title='Upload or delete a photo',
        description='Uploads or deletes a photo using the given auth token.',
        dest='action',
    )
    sp_upload = sp.add_parser('upload', help='Uploads a photo.')
    sp_upload.add_argument('-p', '--photo', required=True, help='Path to the photo to upload.')
    sp_upload.add_argument('-u', '--user_id', required=True, help='User ID for owner.')
    sp_delete = sp.add_parser('delete', help='Deletes a photo.')
    sp_delete.add_argument('-k', '--key', required=True, help='Key of the photo to delete.')
    sp_confirm = sp.add_parser('confirm', help='Confirms a photo has finished processing.')
    sp_confirm.add_argument('-k', '--key', required=True, help='Key of the photo to confirm.')
    args = parser.parse_args()

    configure_logging(args.verbose)

    token = args.token

    if args.action == 'upload':
        photo = args.photo
        uid = args.user_id
        if isfile(photo):
            upload(token, uid, photo)
        else:
            error(f'Photo [{photo}] does not exist.')

    if args.action == 'delete':
        key = args.key
        delete(token, key)

    if args.action == 'confirm':
        key = args.key
        confirm(token, key)
