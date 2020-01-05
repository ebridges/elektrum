from os import getenv
from django.conf import settings


# noinspection PyUnusedLocal
def selected_settings(request):
    # return the version value as a dictionary
    # you may add other values here as well
    return {
        'APP_VERSION_NUMBER': settings.APP_VERSION_NUMBER,
        'APP_DB_HOST': getenv('DB_HOSTNAME'),
        'APP_NAME': getenv('SERVICE_NAME'),
    }
