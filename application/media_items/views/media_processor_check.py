from logging import info
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view

from base.views.errors import (
    MethodNotAllowedException,
    ForbiddenException,
    exceptions_to_api_response,
)
from media_items.models import MediaItem


@api_view(http_method_names=['HEAD'])
@exceptions_to_api_response
def confirm_upload(request, owner_id, image_id, extension):
    info(f'confirm processing completed for {owner_id}/{image_id}.{extension}')
    validate(request, owner_id)
    return check_exists(image_id)


def check_exists(iid):
    if MediaItem.objects.filter(pk=iid).exists():
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=404)


def validate(request, owner_id):
    if request.method != 'HEAD':
        raise MethodNotAllowedException('HEAD')

    user = request.user
    if not user.is_authenticated:
        raise ForbiddenException('Authentication is required.')

    if not user.id == owner_id:
        raise ForbiddenException('Permission denied')
