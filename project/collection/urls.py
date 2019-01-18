from django.urls import path

from . import views

urlpatterns = [
    path('', views.CollectionList.as_view(), name='collection_list'),
    path('view/<uuid:pk>', views.CollectionView.as_view(), name='collection_view'),
    path('new', views.CollectionCreate.as_view(), name='collection_new'),
    path('edit/<uuid:pk>', views.CollectionUpdate.as_view(), name='collection_edit'),
    path('delete/<uuid:pk>', views.CollectionDelete.as_view(), name='collection_delete'),
]
