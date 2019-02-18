from django.urls import path
from . import views

urlpatterns = [
    path('request-upload/', views.SignRequest.as_view(), name='request-upload'),
]
