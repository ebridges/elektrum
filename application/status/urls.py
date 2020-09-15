from django.urls import path
from status.views.ok import Ok
from status.views.db_create import DBCreate

urlpatterns = [
    path('ok/', Ok.as_view(), name='ok'),
    path('db/create/', DBCreate.as_view(), name='db-create'),
]
