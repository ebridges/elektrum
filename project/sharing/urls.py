from django.urls import path
from sharing.views import sharing_items_view, sharing_list_view


urlpatterns = [
    path('media/', sharing_items_view, name='sharing-items-view'),
    path(
        'list/<uuid:owner_id>/<yyyy:year>/<yyyy-mm-dd:date>/',
        sharing_list_view,
        name='sharing-list-view',
    ),
]
