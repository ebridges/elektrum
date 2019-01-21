from django.urls import path

from . import views

urlpatterns = [
    path('', views.collection_list, name='collection_list'),
    path('view/<uuid:pk>', views.collection_view, name='collection_view'),
    path('new', views.collection_create, name='collection_new'),
    path('edit/<uuid:pk>', views.collection_edit, name='collection_edit'),
    path('delete/<uuid:pk>', views.collection_delete, name='collection_delete'),
]
