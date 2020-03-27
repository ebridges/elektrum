from django.urls import path
from sharing.views import sharing_items_select, sharing_items_list, share_items, shared_items


urlpatterns = [
    path('media/shared-items/<uuid:share_id>/', shared_items, name='shared-items'),
    path('media/share-items/<uuid:share_id>/', share_items, name='share-items'),
    path('media/select-items/', sharing_items_select, name='sharing-items-select'),
    path(
        'media/list-items/<yyyy:year>/<yyyy-mm-dd:date>/',
        sharing_items_list,
        name='sharing-items-list',
    ),
]
