from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from urllib.parse import urlencode, quote_plus
from base.views.errors import exceptions_to_web_response
from media_items.views.media_views import media_list_view
from media_items.models import MediaItem
from sharing.models import Share
from sharing.forms import ShareForm
from base.views.errors import BadRequestException


@exceptions_to_web_response
def sharing_items_list(request, year, date):
    owner_id = request.user.id
    return media_list_view(request, owner_id, year, date, 'sharing/sharing_list_view.html')


@exceptions_to_web_response
def sharing_items_select(request):

    if request.method == 'POST':
        items = request.POST.getlist('items-to-share')

        if len(items) > 0:
            if 'share-id' in request.POST:
                share = Share.objects.get(pk=request.POST['share-id'])
            else:
                share = Share(shared_by=request.user)
                share.save()

            for item in items:
                share.shared.add(MediaItem.objects.get(pk=item))

            url = reverse('share-items', kwargs={'share_id': share.id})

            return redirect(url)
        else:
            # handle state where no items selected
            pass
    else:
        # handle unsupported method
        pass


@exceptions_to_web_response
def share_items(request, share_id):
    if not share_id:
        raise BadRequestException('Share not identified.')

    share = get_object_or_404(Share, pk=share_id)
    items = [item.view() for item in share.shared.all()]
    item_ids = [item.id for item in share.shared.all()]

    if request.method == 'POST':
        action = request.POST['action']
        form = ShareForm(
            request.POST,
            initial={
                'from_address': request.user.email,
                'subject_line': 'Sharing %s images from elektrum.' % len(items),
            },
        )

        if form.is_valid():
            if action == 'share':
                return do_share_items(request.user, share, form.cleaned_data)

            elif action == 'draft':
                return do_save_draft()

            elif action == 'cancel':
                return do_cancel_share()

            else:
                # handle unrecognized value for 'action'
                return JsonResponse(data={'response': 'ok (unrecognized action)'})
    else:
        form = ShareForm(
            initial={
                'from_address': request.user.email,
                'subject_line': 'Sharing %s images from elektrum.' % len(items),
            }
        )

    context = {
        'form': form,
        'objects': items,
        'share_id': share_id,
        'default_emails': [
            'jbond007@mi6.defence.gov.uk',
            'jbourne@unknown.net',
            'nfury@shield.org',
            'tony@starkindustries.com',
            'hulk@grrrrrrrr.arg',
        ],
    }

    return render(request, 'sharing/sharing_items_view.html', context)


def do_share_items(u, s, d):
    return JsonResponse(
        data={'response': 'ok', 'user': {'id': u.id, 'email': u.email}, 'share_id': s.id, 'data': d}
    )


def do_cancel_share():
    pass


def do_save_draft():
    pass
