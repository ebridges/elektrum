from argparse import ArgumentParser
from logging import basicConfig, DEBUG, INFO, debug, info, warning, error
from os.path import isfile, splitext
from pprint import pprint
from sys import argv, exit
from time import sleep
from urllib.parse import urlparse
from requests import post, put, head


MIME_TYPES = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}

UPLOAD_ENDPOINT = 'https://elektrum.dev/media/api/upload-request/'
CONFIRM_ENDPOINT = 'https://elektrum.dev/media/api/confirm-upload'


def upload(token, photo):
    debug(f'Uploading photo {photo}')
    ext = splitext(photo)[1][1:]
    mime_type = MIME_TYPES[ext]
    upload_url, key = upload_request(token, mime_type)

    if not upload_url:
        return None

    info(f'Uploading photo to {key}')
    upload_photo(token, upload_url, key, photo, mime_type)

    confirm(token, key, photo)


def confirm(token, key, photo=None):
    confirm_url = f'{CONFIRM_ENDPOINT}/{key}'
    headers = {'Authorization': f'Bearer {token}'}
    chk_cnt = 0
    while True:
        chk_cnt = chk_cnt + 1
        response = head(confirm_url, headers=headers)
        if response.status_code == 200:
            info(f'Image uploaded to {key} has completed processing.')
            break
        elif response.status_code == 403:
            error('Unauthorized.')
            break
        elif chk_cnt > 60:
            if photo:
                print(f'ERROR:processing-not-completed:{photo}:{key}')
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
            info(f'image uploaded under key {key}')
        else:
            print(f'ERROR:upload-error:{photo}:{key}')
            error(f'Unable to upload [{photo}] under [{key}]: {response.text}')


def upload_request(token, mime_type):
    headers = {'Authorization': f'Bearer {token}'}
    body = {
        'mime_type': mime_type,
    }
    response = post(UPLOAD_ENDPOINT, data=body, headers=headers)
    if response.status_code == 201:
        upload_url = response.headers['location']
        u = urlparse(upload_url)
        key = u.path[1:]
        return upload_url, key
    else:
        print(f'ERROR:upload-request-error:{photo}')
        error(f'Unable to request upload photo url: {response.text}')


def delete(token, key):
    debug(f'Deleting photo {key}')
    raise NotImplementedError()


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
    sp_delete = sp.add_parser('delete', help='Deletes a photo.')
    sp_delete.add_argument('-k', '--key', required=True, help='Key of the photo to delete.')
    sp_confirm = sp.add_parser('confirm', help='Confirms a photo has finished processing.')
    sp_confirm.add_argument('-k', '--key', required=True, help='Key of the photo to confirm.')
    args = parser.parse_args()

    configure_logging(args.verbose)

    token = args.token

    if args.action == 'upload':
        photo = args.photo
        if isfile(photo):
            upload(token, photo)
        else:
            error(f'Photo [{photo}] does not exist.')

    if args.action == 'delete':
        key = args.key
        delete(token, key)

    if args.action == 'confirm':
        key = args.key
        confirm(token, key)
