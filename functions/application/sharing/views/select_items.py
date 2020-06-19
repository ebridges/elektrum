from django.shortcuts import redirect, reverse
from base.views.errors import (
    exceptions_to_web_response,
    MethodNotAllowedException,
    BadRequestException,
)

from media_items.models import MediaItem
from sharing.models import Share


@exceptions_to_web_response
def select_items(request):
    if request.method == 'POST':
        items = request.POST.getlist('items-to-share')

        if len(items) > 0:
            if 'share-id' in request.POST:
                share = Share.objects.get(pk=request.POST['share-id'])
                share.shared_by = request.user
            else:
                share = Share(shared_by=request.user)
                share.save()

            for item in items:
                share.shared.add(MediaItem.objects.get(pk=item))

            url = reverse('share-items', kwargs={'id': share.id})

            return redirect(url)
        else:
            raise BadRequestException('No items selected.')
    else:
        raise MethodNotAllowedException('POST')
