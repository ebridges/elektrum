import re

from django.conf import settings
from django.shortcuts import render

from base.views.errors import exceptions_to_web_response
from base.views.utils import assert_owner_id
from media_items.models import MediaItem


@exceptions_to_web_response
def media_list_view(
    request, owner_id, year, date, template_name='media_items/media_list_view.html'
):
    assert_owner_id(owner_id, request.user.id)

    yyyymmdd = int(re.sub('-', '', date))
    media_items = MediaItem.objects.raw(
        '''select m.*
            from media_item m
            where m.create_day_id = %d
            order by m.create_date'''
        % yyyymmdd
    )

    data = []
    for mi in media_items:
        data.append(mi.view())

    return render(
        request, template_name, {'objects': data, 'yyyymmdd': date, 'year': int(date[:4])}
    )
