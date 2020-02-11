#!/usr/bin/env python3

from os import environ
from sys import argv
from argparse import ArgumentParser
from logging import debug, info, INFO, DEBUG, basicConfig
from urllib.parse import urlparse
from datetime import datetime

import requests

# from botocore.vendored import requests
import boto3
from botocore.client import Config


def create_signed_url(bucket_name, file):
    access_key = environ['AWS_ACCESS_KEY_ID']
    access_secret = environ['AWS_SECRET_ACCESS_KEY']
    print(f'access_key: {access_key}, access_secret: {access_secret}')
    now = datetime.utcnow().timestamp()
    upload_key = f'test/{now}-{file}'

    info(f'bucket: {bucket_name}, upload_key: {upload_key}')
    info(f'access_key: {access_key}, access_secret: {access_secret}')

    s3_client = boto3.client(
        's3',
        # aws_access_key_id=access_key,
        # aws_secret_access_key=access_secret,
        config=Config(signature_version='s3v4'),
    )

    info(f's3 client: [{s3_client}]')

    url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': upload_key},
        ExpiresIn=360000,
        HttpMethod='PUT',
    )

    return urlparse(url).geturl()


def upload_photo(photo, url):
    headers = {'Content-type': 'image/jpeg'}
    data = open(photo, 'rb')
    response = requests.put(url, data=data, headers=headers)
    debug(
        'RESPONSE: {status_code}\n{headers}\n\n{body}'.format(
            status_code=response.status_code,
            headers='\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
            body=response.content,
        )
    )


def app(photo, bucket, filename):
    upload_url = create_signed_url(bucket, filename)
    info(f'Uploading photo to URL: [{upload_url}]')
    upload_photo(photo, upload_url)


def main(argv):
    parser = ArgumentParser(
        prog=argv[0],
        description='Uploads a photo to the given bucket.  Expects `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to be in the environment.',
    )
    parser.add_argument('-p', '--photo', required=True, help='Photo to upload.')
    parser.add_argument('-b', '--bucket', required=True, help='Bucket to upload to.')
    parser.add_argument(
        '-f', '--filename', required=False, help='Filename of photo at destination.'
    )
    parser.add_argument('--verbose')

    args = parser.parse_args()

    if args.verbose:
        level = DEBUG
    else:
        level = INFO

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=level
    )

    filename = args.filename
    if not filename:
        filename = args.photo

    app(args.photo, args.bucket, filename)


if __name__ == '__main__':
    # environ['AWS_ACCESS_KEY_ID'] = ''
    # environ['AWS_SECRET_ACCESS_KEY'] = ''
    # environ['AWS_DEFAULT_REGION'] = ''

    main(argv)
