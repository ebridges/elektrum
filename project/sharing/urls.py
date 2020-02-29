from django.urls import path
from sharing.views import share_media

urlpatterns = [path('media/', share_media, name='share-media')]
