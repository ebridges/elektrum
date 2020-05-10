from os import environ
from base.views.errors import BadRequestException

DEFAULT_THUMBNAIL_W = 222
DEFAULT_THUMBNAIL_H = 222


def assert_owner_id(owner_id, user_id):
    if owner_id != user_id:
        raise BadRequestException('User is not authenticated properly')


def media_url(path, scheme='https'):
    return '%s://%s/%s' % (scheme, environ.get('MEDIA_STORAGE_CNAME'), path)


def thumbnail_url(path, scheme='https'):
    return '%s://%s/%s/%s/%s' % (
        scheme,
        environ.get('THUMBNAIL_DOMAIN_NAME'),
        DEFAULT_THUMBNAIL_W,
        DEFAULT_THUMBNAIL_H,
        path,
    )
