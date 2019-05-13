from django.shortcuts import render, redirect, get_object_or_404

from base.views.errors import *
from media_items.models import MediaItem
from date_dimension.models import DateDimension


def media_item_view():
    pass


def media_list_view():
    pass


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
