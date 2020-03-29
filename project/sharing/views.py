from datetime import datetime
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from urllib.parse import urlencode, quote_plus
from base.views.errors import exceptions_to_web_response
from media_items.views.media_views import media_list_view
from media_items.models import MediaItem
from sharing.models import Share, Audience
from sharing.forms import ShareForm
from base.views.errors import BadRequestException, MethodNotAllowedException
from emailer.utils import send_email


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
        raise MethodNotAllowedException('Method unsupported.')


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
                'to_address': [a.email for a in share.shared_to.all()],
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
    s.shared_to.clear()
    for address in d['to_address']:
        (audience, created) = Audience.objects.get_or_create(email=address)
        s.shared_to.add(audience)
    s.shared_on = datetime.now()
    s.save()

    text_tmpl = 'sharing/email_template.txt'
    html_tmpl = 'sharing/email_template.html'
    context = {
        'to_address': d['to_address'],
        'subject_line': d['subject_line'],
        'share_message': d['share_message'],
        'shared_count': len(s.shared.all()),
        'shared_by': u.name(),
        'shared_on': s.shared_on,
        'objects': [item.view() for item in s.shared.all()],
    }

    send_email(
        u.email,
        d['to_address'],
        d['subject_line'],
        body_text_tmpl=text_tmpl,
        body_html_tmpl=html_tmpl,
        context=context,
    )

    url = reverse('shared-items', kwargs={'share_id': s.id})
    return redirect(url)


def shared_items(request, share_id):
    if not share_id:
        raise BadRequestException('Share not identified.')

    share = get_object_or_404(Share, pk=share_id)
    items = [item.view() for item in share.shared.all()]
    context = {
        'objects': items,
        'to_address': [a.email for a in share.shared_to.all()],
        'shared_on': str(share.shared_on),
    }
    return render(request, 'sharing/sharing_items_shared.html', context)


def do_cancel_share():
    pass


def do_save_draft():
    pass
