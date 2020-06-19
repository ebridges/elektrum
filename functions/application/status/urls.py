from django.urls import path
from . import views

urlpatterns = [
    path('ok/', views.Ok.as_view(), name='ok'),
    path('db/create/', views.DBCreate.as_view(), name='db-create'),
]
