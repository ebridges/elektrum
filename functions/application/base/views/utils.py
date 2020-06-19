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
    if environ['ENVIRONMENT'] == 'local':
        path = path.replace('/', '%2f')
        return f'http://localhost:8182/iiif/2/{path}/square/{DEFAULT_THUMBNAIL_W},{DEFAULT_THUMBNAIL_H}/0/default.jpg'
    else:
        return '%s://%s/%s/%s/%s' % (
            scheme,
            environ.get('THUMBNAIL_DOMAIN_NAME'),
            DEFAULT_THUMBNAIL_W,
            DEFAULT_THUMBNAIL_H,
            path,
        )


def format_sql(sql):
    '''
    Convert SQL that's written across multiple lines for legibility to a single line for better logging.
    Replaces newlines with a single space, and then compresses multiple spaces to a single space.
    '''
    return ' '.join(sql.replace('\n', ' ').split())
