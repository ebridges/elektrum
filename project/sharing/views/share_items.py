from datetime import datetime
from logging import info

from django.db.models import Count
from django.shortcuts import render, redirect, reverse, get_object_or_404

from base.views.errors import exceptions_to_web_response, BadRequestException
from emailer.views import send_email
from sharing.models import Share, Audience, ShareState
from sharing.forms import ShareForm
from sharing.views.common import do_delete_share


@exceptions_to_web_response
def share_items(request, id):
    info(f'share_items({id})')
    if not id:
        raise BadRequestException('Share not identified.')

    share = get_object_or_404(Share, pk=id)
    if share.state == ShareState.SHARED:
        # this has already been shared, so redirect to a read only view
        url = reverse('share-log-item', kwargs={'id': share.id})
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
        'id': id,
        'default_emails': default_emails,
    }

    return render(request, 'sharing/share_items.html', context)


def default_email_list(uid):
    '''
    Builds a list of the top 10 email addresses that this user has shared to, sorted alphabetically.
    '''
    top_emails = (
        Audience.objects.filter(shared_by=uid, unsubscribed=False)
        .values('email')
        .annotate(shares=Count('audienceshare'))
        .order_by('-shares')[:10]
    )

    emails = []
    for e in top_emails:
        emails.append(e['email'])
    return sorted(emails)


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

        url = reverse('share-log-item', kwargs={'id': share.id})
        return redirect(url)
    else:
        # handle case where there are no "to" emails or no images selected
        raise BadRequestException('no "to" addresses and/or no images selected.')


def do_save_draft(user, share, data):
    share.from_data(data)
    share.state = ShareState.DRAFT
    share.save()
    url = reverse('collections-view', kwargs={'owner_id': user.id})
    return redirect(url)
