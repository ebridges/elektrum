from django.shortcuts import render, get_object_or_404

from base.views.errors import exceptions_to_web_response
from sharing.models import Audience


@exceptions_to_web_response
def unsubscribe(request, email_id):
    email = get_object_or_404(Audience, pk=email_id)
    owner = email.shared_by
    context = {'shared_to': email.email, 'shared_by': owner.name(), 'email_id': email.id}

    if request.method == 'POST':
        email.unsubscribed = True
        email.save()
        context['unsubscribed'] = True

    return render(request, 'emailer/unsubscribe.html', context)
