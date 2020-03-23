from django.shortcuts import render, redirect, reverse
from urllib.parse import urlencode, quote_plus
from base.views.errors import exceptions_to_web_response
from media_items.views.media_views import media_list_view
from media_items.models import MediaItem
from sharing.models import Share
from base.views.errors import BadRequestException


@exceptions_to_web_response
def sharing_list_view(request, owner_id, year, date):
    return media_list_view(request, owner_id, year, date, 'sharing/sharing_list_view.html')


@exceptions_to_web_response
def sharing_items_view(request):
    if request.method == 'GET':
        # else if request.method == 'GET':
        # query items to share, and render page with data
        share_id = request.GET.get('share-id')
        if not share_id:
            raise BadRequestException('Share not identified.')

        share = Share.objects.get(pk=share_id)
        items = [item.view() for item in share.shared.all()]
        response_data = {'objects': items, 'share_id': share.id}

        return render(request, 'sharing/sharing_items_view.html', response_data)

    elif request.method == 'POST':
        items = request.POST.getlist('items-to-share')

        if len(items) > 0:
            if 'share-id' in request.POST:
                share = Share.objects.get(pk=request.POST['share-id'])
            else:
                share = Share(shared_by=request.user)
                share.save()

            for item in items:
                share.shared.add(MediaItem.objects.get(pk=item))

            url = reverse('sharing-items-view')
            qs = urlencode({'share-id': share.id}, quote_via=quote_plus)
            response_url = f'{url}?{qs}'

            return redirect(response_url)
        else:
            # handle state where no items selected
            pass
    else:
        # handle unsupported method
        pass


@exceptions_to_web_response
def share_items(request):
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'share':
            response = do_share_items()

        elif action == 'draft':
            response = do_save_draft()

        elif action == 'cancel':
            response = do_cancel_share()

        else:
            # handle unrecognized value for 'action'
            pass

        return response


def do_share_items():
    pass


def do_cancel_share():
    pass


def do_save_draft():
    pass
