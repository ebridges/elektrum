from os import getenv
from django.conf import settings

from base.views.utils import DEFAULT_THUMBNAIL_W, DEFAULT_THUMBNAIL_H


# noinspection PyUnusedLocal
def selected_settings(request):
    # return the version value as a dictionary
    # you may add other values here as well
    return {
        'APP_VERSION_NUMBER': settings.APP_VERSION_NUMBER,
        'APP_DB_HOST': getenv('DB_HOSTNAME'),
        'APP_NAME': getenv('SERVICE_NAME'),
        'THUMBNAIL_WIDTH': DEFAULT_THUMBNAIL_W,
        'THUMBNAIL_HEIGHT': DEFAULT_THUMBNAIL_H,
    }
