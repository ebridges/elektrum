from django.shortcuts import render

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views import View
from django.utils.dateparse import parse_datetime

from media_items.upload_signing import create_signed_upload_url, supported_upload_types


class SignRequest(View):
    http_method_names = ['post']

    @staticmethod
    def post(request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden(content='Authentication is required.')

        if 'mime_type' not in request.POST:
            return HttpResponseBadRequest('"mime_type" is a required parameter. It should be parsed from media\'s '
                                          'metadata.')

        mime_type = request.POST['mime_type']
        if mime_type not in supported_upload_types:
            return HttpResponseBadRequest('the provided mime type [%s] is not supported.' % mime_type)

        signed_url = create_signed_upload_url(user, mime_type)

        response = HttpResponse(status=201)
        response['Location'] = signed_url.geturl()

        return response
