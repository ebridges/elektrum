from django.urls import path

from sharing.views.list_items import list_items
from sharing.views.share_items import share_items
from sharing.views.share_log_delete import share_log_delete
from sharing.views.share_log import share_log
from sharing.views.share_log_item import share_log_item
from sharing.views.select_items import select_items


urlpatterns = [
    path('list-items/<yyyy:year>/<yyyy-mm-dd:date>/', list_items, name='list-items'),
    path('select-items/', select_items, name='select-items'),
    path('share-items/<uuid:id>/', share_items, name='share-items'),
    path('share-log/', share_log, name='share-log'),
    path('share-log/<uuid:id>/', share_log_item, name='share-log-item'),
    path('share-log/delete/<uuid:id>/', share_log_delete, name='share-log-delete'),
]
