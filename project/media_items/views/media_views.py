import re

from django.shortcuts import render, redirect, get_object_or_404

from base.views.utils import assert_owner_id, media_url
from base.views.errors import exceptions_to_http_status, BadRequestException
from media_items.models import MediaItem
from date_dimension.models import DateDimension


@exceptions_to_http_status
def media_item_view(request, owner_id, image_id, template_name='media_items/media_item_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_item = get_object_or_404(MediaItem, id=image_id)
    data = { 
        'collection_year': media_item.create_day.year, 
        'album_id': media_item.create_day.iso_date, 
        'media_item': media_item, 
        'media_item_url': media_url(media_item.file_path) 
    }
    return render(request, template_name, data)


@exceptions_to_http_status
def media_list_view(request, owner_id, year, date, template_name='media_items/media_list_view.html'):
    assert_owner_id(owner_id, request.user.id)

    yyyymmdd = int(re.sub('-', '', date))
    media_items = MediaItem.objects.raw('''select m.* 
                                           from media_item m
                                           where m.create_day_id = %d
                                           order by m.create_date''' % yyyymmdd)

    data = []
    for mi in media_items:
        data.append({'file_name': mi.create_day_id, 'url': media_url(mi.file_path), 'title': mi.create_date, 'item_id': mi.id})

    return render(request, template_name, {'objects': data, 'yyyymmdd': date, 'year': int(date[:4])})


@exceptions_to_http_status
def albums_view(request, owner_id, year, template_name='media_items/albums_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_items = MediaItem.objects.raw('''select distinct on (d.yyyymmdd) m.* 
                                           from media_item m, date_dim d 
                                           where m.create_day_id = d.yyyymmdd 
                                           and d.year = %d
                                           order by d.yyyymmdd, random()''' % year)

    data = []
    for mi in media_items:
        data.append({'yyyymmdd': yyyy_mm_dd(str(mi.create_day_id)), 'url': media_url(mi.file_path)})

    return render(request, template_name, {'objects': data, 'year': int(str(mi.create_day_id)[:4])})


@exceptions_to_http_status
def collections_view(request, owner_id, template_name='media_items/collections_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_items = MediaItem.objects.raw('''select distinct on (d.year) m.* 
                                    from media_item m, date_dim d 
                                    where m.create_day_id = d.yyyymmdd 
                                    order by d.year, random()''')
    data = []
    for mi in media_items:
        data.append({'year': int(str(mi.create_day_id)[:4]), 'url': media_url(mi.file_path)})

    return render(request, template_name, {'objects': data})


def yyyy_mm_dd(val):
    return '%s-%s-%s' % (val[0:4], val[4:6], val[6:8])
