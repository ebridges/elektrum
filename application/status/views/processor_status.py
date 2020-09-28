from json import loads

from django.shortcuts import render
from django import forms
from rest_framework.response import Response
from rest_framework.decorators import api_view

from base.views.errors import (
    MethodNotAllowedException,
    ForbiddenException,
    exceptions_to_web_response,
    exceptions_to_api_response,
)
from status.models import ProcessorLog, ProcessorLogForm


@exceptions_to_web_response
def processor_log(request):
    log = ProcessorLog.objects.filter(owner=request.user).order_by('-event_date')
    context = {'processor_log_list': log}
    return render(request, 'status/processor_log.html', context)


@exceptions_to_web_response
def processor_log_delete(request, id):
    log = ProcessorLog.objects.get(id=id)
    log.delete()
    return processor_log(request)


@api_view(http_method_names=['POST'])
@exceptions_to_api_response
def processor_log_item(request):
    validate_request(request)
    data = loads(request.body)
    form = ProcessorLogForm(data=data)
    if form.is_valid():
        form.save()
        return Response(None, status=201)
    else:
        eee = {'validation_errs': loads(form.errors.as_json())}
        raise ValueError(eee)


def validate_request(request, owner_id):
    if request.method != 'POST':
        raise MethodNotAllowedException('POST')

    user = request.user
    if not user.is_authenticated:
        raise ForbiddenException('Authentication is required.')

    if user.id != owner_id:
        raise ForbiddenException('Unauthorized')
