from django.urls import path, register_converter

from media_items.views.albums_view import albums_view
from media_items.views.collections_view import collections_view
from media_items.views.media_list_view import media_list_view
from media_items.views.media_item_view import media_item_view
from media_items.views.media_item_upload_view import media_item_upload_view
from media_items.views.upload_request import upload_request_web, upload_request_api
from media_items.views.media_processor_check import confirm_upload


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
    path('upload-request/', upload_request_web, name='upload-request'),
    path('api/upload-request/', upload_request_api, name='upload-request-api'),
    path('api/confirm-upload/<uuid:uid>/<uuid:iid>.<ext>', confirm_upload, name='confirm-upload'),
    path('<uuid:owner_id>/upload/', media_item_upload_view, name='media-item-upload-view'),
    path('<uuid:owner_id>/<uuid:image_id>/', media_item_view, name='media-item-view'),
    path('<uuid:owner_id>/<yyyy:year>/<yyyy-mm-dd:date>/', media_list_view, name='media-list-view'),
    path('<uuid:owner_id>/<yyyy:year>/', albums_view, name='albums-view'),
    path('<uuid:owner_id>/', collections_view, name='collections-view'),
]
