from django.urls import path

from . import views

urlpatterns = [
    path('list/<uuid:collection>', views.album_list, name='album_list'),
    path('view/<uuid:pk>', views.album_view, name='album_view'),
    path('new', views.album_create, name='album_new'),
    path('edit/<uuid:pk>', views.album_edit, name='album_edit'),
    path('delete/<uuid:pk>', views.album_delete, name='album_delete'),
]
