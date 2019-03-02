import os
import boto3
import string
import random
from pathlib import PurePath
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation

from media_items.models import MediaItem

supported_upload_types = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
}


def record_upload_request(user, upload_url, mime_type):
    """
    Records an upload request so that after the upload has been completed, the media processing pipeline
    can enrich this record with metadata about the media_item.

    :param user:
    :param upload_url:
    :param mime_type:
    :return: id of newly created item
    """
    u = urlparse(upload_url)
    user_id, file_path = split_upload_path(u.path)
    if user_id != str(user.id):
        # This id should correspond to the current logged in user.
        raise SuspiciousOperation('ID in path not found.')
    item = MediaItem.objects.create(
        owner=user,
        path=file_path,
        media_type=mime_type
    )
    item.save()
    return item.id


def split_upload_path(upload_path):
    """
    Given a path of the form:
    /[USER_ID]/2020/2020-02-26/2020-02-26T112343_[SLUG].jpg
    Returns a tuple of the form: (user_id, file_path), where:
    user_id: [USER_ID]
    file_path: /2020/2020-02-26/2020-02-26T112343_[SLUG].jpg

    :param upload_path:
    :return: tuple
    """
    p = PurePath(upload_path.strip('/'))
    return p.parts[0], os.path.join('/', *p.parts[1:])


def create_signed_upload_url(user, create_date, mime_type):
    """
    :param user:
    :param create_date:
    :param mime_type:
    :return: URL used for direct upload to S3

    Example returned URL:
    https://[BUCKET].s3.amazonaws.com/[USER_ID]/2020/2020-02-26/2020-02-26T112343_[SLUG].jpg
    ?AWSAccessKeyId=[KEY]&Signature=[SIG]&Expires=1550426152
    """
    access_credentials = lookup_user_upload_credentials(user)

    upload_key = create_upload_key(user, create_date, mime_type)

    return create_signed_url(access_credentials, upload_key)


def create_signed_url(credentials, upload_key):
    """
    Given credentials and a storage key, generate a signed URL to upload the item with.

    :param credentials:
    :param upload_key:
    :return:
    """
    access_key, access_secret, bucket_name = credentials
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=access_secret)
    s3client = session.client('s3')
    url = s3client.generate_presigned_url('put_object', Params={'Bucket': bucket_name, 'Key': upload_key})
    return url


def create_upload_key(user, created, mtype, slug=None):
    """
    Given a user and a date, generate a key to name the uploaded media. Form of the key:
    `userID/yyyy/yyyy-mm-dd/yyyymmddThhmmss_uuid[8].ext`

    :param user:
    :param created:
    :param mtype:
    :param slug:
    :return:
    """
    year = created.strftime('%Y')
    date = created.strftime('%Y-%m-%d')
    iso_date = created.strftime('%Y-%m-%d''T''%H%M%S')
    if not slug:
        slug = generate_slug()
    extension = extension_from_type(mtype)

    return '%s/%s/%s/%s_%s.%s' % (user.id, year, date, iso_date, slug, extension)


def lookup_user_upload_credentials(user):
    """
    Obtains the upload credentials and bucket for the given user.

    :param user:
    :return:
    """
    # @todo: update this to retrieve these values from the user's profile.
    aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    aws_upload_bucket_name = os.environ['AWS_UPLOAD_BUCKET_NAME']
    return aws_access_key, aws_secret_access_key, aws_upload_bucket_name


def generate_slug(size=8, chars=string.ascii_lowercase + string.digits):
    """
    Generate an `n` char random string.

    :return:
    """
    return ''.join(random.choice(chars) for _ in range(size))


def extension_from_type(mtype):
    """
    From a statically defined list of types, return the corresponding extension for it.

    :param mtype:
    :return:
    """
    return supported_upload_types[mtype]
