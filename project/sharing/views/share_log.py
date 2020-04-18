from django.shortcuts import render

from base.views.errors import exceptions_to_web_response
from sharing.models import Share


@exceptions_to_web_response
def share_log(request):
    shares = Share.objects.filter(shared_by=request.user).order_by('-modified')
    context = {'share_list': shares}
    return render(request, 'sharing/share_log.html', context)
