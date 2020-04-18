from logging import info

from django.shortcuts import render, get_object_or_404

from base.views.errors import exceptions_to_web_response, BadRequestException
from sharing.models import Share


@exceptions_to_web_response
def share_log_item(request, id=None):
    info(f'share_log_item({id})')
    if not id:
        raise BadRequestException('Share not identified.')
    share = get_object_or_404(Share, pk=id)
    context = {'share': share.view(), 'objects': share.view()['shared']}
    return render(request, 'sharing/share_log_item.html', context)
