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
    access_credentials = lookup_user_upload_credentials(user)

    upload_key = create_upload_key(user, mime_type)

    url = create_signed_url(access_credentials, upload_key)

    location = url.geturl()
    logger = getLogger(__name__)
    logger.info('signed request url: %s' % location)

    return location


def create_signed_url(credentials, upload_key):
    """
    Given credentials and a storage key, generate a signed URL to upload the item with.

    :param credentials:
    :param upload_key:
    :return:
    """
    access_key, access_secret, bucket_name = credentials

    logger = getLogger(__name__)
    logger.info(f'access_key: {access_key}, access_secret: {access_secret}')
    s3client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=access_secret,
        config=Config(signature_version='s3v4'),
    )

    url = s3client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': upload_key},
        ExpiresIn=360000,
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


# noinspection PyUnusedLocal
def lookup_user_upload_credentials(user):
    """
    Obtains the upload credentials and bucket for the given user.

    :param user:
    :return:
    """
    # @todo: update this to retrieve these values from the user's profile.
    aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    aws_upload_bucket_name = os.environ['MEDIA_UPLOAD_BUCKET_NAME']
    return aws_access_key, aws_secret_access_key, aws_upload_bucket_name


def extension_from_type(mtype):
    """
    From a statically defined list of types, return the corresponding extension for it.

    :param mtype:
    :return:
    """
    return supported_upload_types[mtype]
