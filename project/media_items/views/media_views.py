from django.shortcuts import render, redirect, get_object_or_404

from base.views.errors import exceptions_to_http_status, BadRequestException
from media_items.models import MediaItem
from date_dimension.models import DateDimension


@exceptions_to_http_status
def media_item_view(request, owner_id, image_id, template_name='media_items/media_item_view.html'):
    assert_owner_id(owner_id, request.user.id)
    media_item = get_object_or_404(MediaItem, id=image_id)
    data = {'media_item': media_item}
    return render(request, template_name, data)


@exceptions_to_http_status
def media_list_view(request, owner_id, year, date, template_name='media_items/media_list_view.html'):
    assert_owner_id(owner_id, request.user.id)
    dates = DateDimension.objects.filter(mediaitem__owner_id__exact=owner_id, year__exact=year, iso_date__exact=date)
    media_items = MediaItem.objects.filter(owner_id__exact=owner_id, create_day__iso_date__exact=date)
    data = {'object_list': media_items, 'collection_year': year, 'album_dates': dates}
    return render(request, template_name, data)


@exceptions_to_http_status
def albums_view(request, owner_id, year, template_name='media_items/albums_view.html'):
    assert_owner_id(owner_id, request.user.id)
    dates = DateDimension.objects.filter(mediaitem__owner_id__exact=owner_id, year__exact=year)
    data = {'object_list': [d.yyyymmdd for d in dates], 'collection_year': year}
    return render(request, template_name, data)


@exceptions_to_http_status
def collections_view(request, owner_id, template_name='media_items/collections_view.html'):
    assert_owner_id(owner_id, request.user.id)
    dates = DateDimension.objects.filter(mediaitem__owner_id__exact=owner_id)
    data = {'object_list': [d.year for d in dates]}
    return render(request, template_name, data)


def assert_owner_id(owner_id, user_id):
    if owner_id != user_id:
        raise BadRequestException('User is not authenticated properly')
