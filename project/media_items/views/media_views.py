import re

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from base.views.utils import assert_owner_id, media_url
from base.views.errors import exceptions_to_web_response, BadRequestException
from media_items.models import MediaItem
from date_dimension.models import DateDimension


@exceptions_to_web_response
def media_item_upload_view(
    request, owner_id, template_name='media_items/media_item_upload_view.html'
):
    assert_owner_id(owner_id, request.user.id)
    return render(request, template_name)


@exceptions_to_web_response
def media_item_view(request, owner_id, image_id, template_name='media_items/media_item_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_item = get_object_or_404(MediaItem, id=image_id)
    data = {
        'collection_year': media_item.create_day.year,
        'album_id': media_item.create_day.iso_date,
        'media_item': media_item,
        'media_item_url': media_url(media_item.file_path),
    }
    return render(request, template_name, data)


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
        data.append(
            {
                'file_name': mi.create_day_id,
                'url': media_url(mi.file_path),
                'title': mi.create_date,
                'item_id': mi.id,
            }
        )

    return render(
        request, template_name, {'objects': data, 'yyyymmdd': date, 'year': int(date[:4])}
    )


@exceptions_to_web_response
def albums_view(request, owner_id, year, template_name='media_items/albums_view.html'):
    assert_owner_id(owner_id, request.user.id)

    # Query to get a random item for the given year.  Query is postgres-specific,
    # so when running test, use a different query.  Caveat, the SQLite query is not
    # equivalent in that it doesn't retrieve a random item. However it is sufficient
    # for current state of tests.
    if not settings.IN_TEST_MODE:
        query = (
            '''select distinct on (d.yyyymmdd) m.*
                   from media_item m, date_dim d
                   where m.create_day_id = d.yyyymmdd
                   and d.year = %d
                   order by d.yyyymmdd, random()'''
            % year
        )
    else:
        query = '''SELECT d.yyyymmdd, m.*
                   from media_item m, date_dim d
                   left JOIN date_dim dd
                   ON
                      d.yyyymmdd < dd.yyyymmdd
                   where
                      dd.yyyymmdd is null
                   '''

    media_items = MediaItem.objects.raw(query)

    data = []
    mi = None
    for mi in media_items:
        data.append({'yyyymmdd': yyyy_mm_dd(str(mi.create_day_id)), 'url': media_url(mi.file_path)})

    return render(request, template_name, {'objects': data, 'year': int(str(mi.create_day_id)[:4])})


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
        data.append({'year': int(str(mi.create_day_id)[:4]), 'url': media_url(mi.file_path)})

    return render(request, template_name, {'objects': data})


def yyyy_mm_dd(val):
    return '%s-%s-%s' % (val[0:4], val[4:6], val[6:8])
