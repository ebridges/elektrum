from django.urls import path, register_converter
from media_items.views.media_views import *
from media_items.views.request_signing import *


# noinspection PyMethodMayBeStatic
class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value


# noinspection PyMethodMayBeStatic
class PathDateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(PathDateConverter, 'yyyy-mm-dd')
register_converter(FourDigitYearConverter, 'yyyy')


urlpatterns = [
    path('request-upload/', upload_media_web, name='request-upload'),
    path('api/request-upload/', upload_media_api, name='request-upload-api'),
    path('<uuid:owner_id>/upload/', media_item_upload_view, name='media-item-upload-view'),
    path('<uuid:owner_id>/<uuid:image_id>/', media_item_view, name='media-item-view'),
    path('<uuid:owner_id>/<yyyy:year>/<yyyy-mm-dd:date>/', media_list_view, name='media-list-view'),
    path(
        'share/<uuid:owner_id>/<yyyy:year>/<yyyy-mm-dd:date>/',
        sharing_list_view,
        name='sharing-list-view',
    ),
    path('<uuid:owner_id>/<yyyy:year>/', albums_view, name='albums-view'),
    path('<uuid:owner_id>/', collections_view, name='collections-view'),
]
