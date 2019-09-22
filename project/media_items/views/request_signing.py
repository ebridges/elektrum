from django.shortcuts import render

from rest_framework.response import Response
from django.http import HttpResponse

from media_items.upload_signing import create_signed_upload_url, supported_upload_types
from elektrum.log import getLogger
from base.errors import *


@exceptions_to_web_response
def upload_media_web(request):
    validate_request(request)

    signed_url = create_signed_upload_url(user, mime_type)

    location = signed_url.geturl()
    logger = getLogger(__name__)
    logger.info('signed request url: %s' % location)

    response = HttpResponse(status=201)
    response['Access-Control-Expose-Headers'] = 'Location'
    response['Location'] = location
    return response


@api_view(http_method_names=['POST'])
@exceptions_to_api_response
def upload_media_api(request):
    validate_request(request)

    signed_url = create_signed_upload_url(user, mime_type)

    location = signed_url.geturl()
    logger = getLogger(__name__)
    logger.info('signed request url: %s' % location)

    headers = {
        'Access-Control-Expose-Headers': 'Location',
        'Location': location
    }
    return Response(None, headers=headers, status=201);


def validate_request(request):
    if request.method != 'POST':
        raise MethodNotAllowedException()
    
    user = request.user
    if not user.is_authenticated:
        raise ForbiddenException(content='Authentication is required.')

    if 'mime_type' not in request.POST:
        raise BadRequestException('"mime_type" is a required parameter. It should be parsed from media\'s '
                                        'metadata.')

    mime_type = request.POST['mime_type']
    if mime_type not in supported_upload_types:
        raise BadRequestException('the provided mime type [%s] is not supported.' % mime_type)
