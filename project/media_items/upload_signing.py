import os
import boto3
from uuid import uuid4
from urllib.parse import urlparse
from botocore.client import Config
from elektrum.log import getLogger

supported_upload_types = {'image/jpeg': 'jpg', 'image/png': 'png'}


def create_signed_upload_url(user, mime_type):
    """
    :param user:
    :param mime_type:
    :return: URL used for direct upload to S3

    Example returned URL:
    http://[BUCKET_NAME].s3.amazonaws.net/[USER_ID]/[UUID4].[EXT]?
    AWSAccessKeyId=[ACCESS_KEY_ID]&Signature=[SIGNATURE]&Expires=[EXPIRY]
    """
    bucket_name = os.environ['MEDIA_UPLOAD_BUCKET_NAME']

    upload_key = create_upload_key(user, mime_type)

    url = create_signed_url(bucket_name, upload_key)

    location = url.geturl()
    logger = getLogger(__name__)
    logger.info('signed request url: %s' % location)

    return location


def create_signed_url(bucket_name, upload_key):
    """
    Given credentials and a storage key, generate a signed URL to upload the item with.

    :param credentials:
    :param upload_key:
    :return:
    """

    s3client = boto3.client('s3', config=Config(signature_version='s3v4'))

    url = s3client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': upload_key},
        ExpiresIn=3600,
        HttpMethod='PUT',
    )
    return urlparse(url)


def create_upload_key(user, mtype):
    """
    Generate a key to name the uploaded media. Form of the key: `userID/uuid4.ext`

    :param user:
    :param mtype:
    :return:
    """
    extension = extension_from_type(mtype)
    return '%s/%s.%s' % (user.id, uuid4(), extension)


def extension_from_type(mtype):
    """
    From a statically defined list of types, return the corresponding extension for it.

    :param mtype:
    :return:
    """
    return supported_upload_types[mtype]
