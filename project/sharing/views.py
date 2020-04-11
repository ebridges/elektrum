from logging import info
from datetime import datetime
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from urllib.parse import urlencode, quote_plus
from base.views.errors import exceptions_to_web_response
from media_items.views.media_views import media_list_view
from media_items.models import MediaItem
from sharing.models import Share, Audience
from sharing.forms import ShareForm
from base.views.errors import BadRequestException, MethodNotAllowedException
from emailer.views import send_email
from sharing.models import ShareState


@exceptions_to_web_response
def sharing_items_list(request, year, date):
    owner_id = request.user.id
    return media_list_view(request, owner_id, year, date, 'sharing/sharing_list_view.html')


@exceptions_to_web_response
def share_log(request):
    shares = Share.objects.filter(shared_by=request.user).order_by('-modified')
    context = {'share_list': shares}
    return render(request, 'sharing/share_log.html', context)


@exceptions_to_web_response
def share_log_item_delete(request, share_id=None):
    info(f'share_log_item_delete({share_id})')
    if not share_id:
        raise BadRequestException('Share not identified.')
    share = Share.objects.get(pk=share_id)
    return do_delete_share(share)


@exceptions_to_web_response
def share_log_item(request, share_id=None):
    info(f'share_log_item({share_id})')
    if not share_id:
        raise BadRequestException('Share not identified.')
    share = get_object_or_404(Share, pk=share_id)
    context = {'share': share.view(), 'objects': share.view()['shared']}
    return render(request, 'sharing/share_log_item.html', context)


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
            share.state = 20  # "draft"

            url = reverse('share-items', kwargs={'share_id': share.id})

            return redirect(url)
        else:
            # handle state where no items selected
            pass
    else:
        raise MethodNotAllowedException('Method unsupported.')


@exceptions_to_web_response
def share_items(request, share_id):
    info(f'share_items({share_id})')
    if not share_id:
        raise BadRequestException('Share not identified.')

    share = get_object_or_404(Share, pk=share_id)
    if share.state == ShareState.SHARED:
        # this has already been shared, so redirect to a read only view
        url = reverse('share-log-item', kwargs={'share_id': share.id})
        return redirect(url)

    if request.method == 'POST':
        action = request.POST['action']
        form = ShareForm(
            request.POST, initial={'from_id': request.user.id, 'from_address': request.user.email}
        )

        info(f'sharing action: {action}')
        if form.is_valid():
            if action == 'share':
                return do_share_items(request.user, share, form.cleaned_data)

            elif action == 'draft':
                return do_save_draft(request.user, share, form.cleaned_data)

            elif action == 'cancel':
                return do_delete_share(share)

            else:
                raise BadRequestException('Unrecognized action.')
        else:
            # falls through to populate default emails and to
            # render view again with warning messages
            pass
    else:
        form = ShareForm(
            initial={
                'from_id': request.user.id,
                'from_address': request.user.email,
                'subject_line': 'Sharing %s images from elektrum.' % share.shared_count(),
                'to_address': [a.email for a in share.shared_to.all()],
                ### TODO -- missing other fields?
            }
        )

    default_emails = default_email_list(request.user.id)

    context = {
        'form': form,
        'objects': [item.view() for item in share.shared.all()],
        'share_id': share_id,
        'default_emails': default_emails,
    }

    return render(request, 'sharing/sharing_items_view.html', context)


def default_email_list(uid):
    '''
    select distinct email, count(sas.share_id)
    from sharing_audience sa
    join sharing_audienceshare sas on sas.shared_to_id = sa.id
    join sharing_share s on sas.share_id = ss.id
    where ss.shared_by_id = ?
    group by sas.share_id
    order by count(sas.share_id) desc
    fetch first 10 rows only
    '''
    return ['aaa@example.com', 'bbb@example.com', 'ccc@example.com', 'ddd@example.com']


def do_share_items(
    user,
    share,
    data,
    text_tmpl='sharing/email_template.txt',
    html_tmpl='sharing/email_template.html',
):
    info('do_share_items() called')
    share.from_data(data, shared_on=datetime.now)
    mail_info = share.view()
    if len(mail_info['to'].items()) > 0 and len(mail_info['shared'].items()) > 0:
        send_email(mail_info, text_tmpl, html_tmpl)

        share.state = ShareState.SHARED
        share.save()

        url = reverse('share-log-item', kwargs={'share_id': share.id})
        return redirect(url)
    else:
        # handle case where there are no "to" emails or no images selected
        raise BadRequestException('no "to" addresses and/or no images selected.')


def do_delete_share(share):
    share.delete()
    url = reverse('share-log')
    return redirect(url)


def do_save_draft(user, share, data):
    share.from_data(data)
    share.state = ShareState.DRAFT
    share.save()
    url = reverse('collections-view', kwargs={'owner_id': user.id})
    return redirect(url)
