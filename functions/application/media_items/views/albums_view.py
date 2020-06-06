from django.conf import settings
from django.shortcuts import render

from base.views.errors import exceptions_to_web_response
from base.views.utils import assert_owner_id, format_sql
from media_items.models import MediaItem


@exceptions_to_web_response
def albums_view(request, owner_id, year, template_name='media_items/albums_view.html'):
    assert_owner_id(owner_id, request.user.id)

    # Query to get a random item for the given year.  Query is postgres-specific,
    # so when running test, use a different query.  Caveat, the SQLite query is not
    # equivalent in that it doesn't retrieve a random item. However it is sufficient
    # for current state of tests.
    if not settings.IN_TEST_MODE:
        query = format_sql(
            '''select distinct on (d.yyyymmdd) m.*
                   from media_item m, date_dim d
                   where m.create_day_id = d.yyyymmdd
                   and d.year = %d
                   order by d.yyyymmdd, random()'''
            % year
        )
    else:
        query = format_sql(
            '''SELECT d.yyyymmdd, m.*
                   from media_item m, date_dim d
                   left JOIN date_dim dd
                   ON
                      d.yyyymmdd < dd.yyyymmdd
                   where
                      dd.yyyymmdd is null
                   '''
        )

    media_items = MediaItem.objects.raw(query)

    data = []
    mi = None
    for mi in media_items:
        data.append(mi.view())

    return render(request, template_name, {'objects': data, 'year': int(str(mi.create_day_id)[:4])})
