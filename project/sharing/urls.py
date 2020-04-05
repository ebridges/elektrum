from django.urls import path
from sharing.views import (
    share_log_item,
    sharing_items_select,
    sharing_items_list,
    share_items,
    share_log,
    share_log_item_delete,
)


urlpatterns = [
    path('media/share-log/<uuid:share_id>/', share_log_item, name='share-log-item'),
    path(
        'media/share-log/delete/<uuid:share_id>/',
        share_log_item_delete,
        name='share-log-item-delete',
    ),
    path('media/share-log/', share_log, name='share-log'),
    path('media/share-items/<uuid:share_id>/', share_items, name='share-items'),
    path('media/select-items/', sharing_items_select, name='sharing-items-select'),
    path(
        'media/list-items/<yyyy:year>/<yyyy-mm-dd:date>/',
        sharing_items_list,
        name='sharing-items-list',
    ),
]
