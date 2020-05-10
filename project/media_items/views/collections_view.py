from django.conf import settings
from django.shortcuts import render

from base.views.errors import exceptions_to_web_response
from base.views.utils import assert_owner_id, media_url
from media_items.models import MediaItem


@exceptions_to_web_response
def collections_view(request, owner_id, template_name='media_items/collections_view.html'):
    assert_owner_id(owner_id, request.user.id)

    # Query to get one random item for each of all years.  Query is postgres-specific,
    # so when running test, use a different query.  Caveat, the SQLite query is not
    # equivalent in that it doesn't retrieve a random item. However it is sufficient
    # for current state of tests.
    if not settings.IN_TEST_MODE:
        query = '''select distinct on (d.year) m.*
                   from media_item m, date_dim d
                   where m.create_day_id = d.yyyymmdd
                   order by d.year, random()'''
    else:
        query = '''SELECT d.year, m.*
                   from media_item m, date_dim d
                   left JOIN date_dim dd
                   ON
                      d.yyyymmdd < dd.yyyymmdd
                   where
                      dd.yyyymmdd is null
                   '''

    media_items = MediaItem.objects.raw(query)
    data = []
    for mi in media_items:
        data.append(mi.view())

    return render(request, template_name, {'objects': data})
