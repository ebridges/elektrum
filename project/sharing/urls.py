from django.urls import path
from sharing.views import share_media, sharing_list_view

urlpatterns = [
    path('media/', share_media, name='share-media'),
    path(
        'list/<uuid:owner_id>/<yyyy:year>/<yyyy-mm-dd:date>/',
        sharing_list_view,
        name='sharing-list-view',
    ),
]
