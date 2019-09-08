from os import environ
from base.views.errors import BadRequestException


def assert_owner_id(owner_id, user_id):
  if owner_id != user_id:
    raise BadRequestException('User is not authenticated properly')


def media_url(path, scheme='https'):
  return '%s://%s/%s' % (scheme, environ.get('media_storage_cname'), path)
