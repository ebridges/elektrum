from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('app-home', views.AppHomePageView.as_view(), name='app-home'),
]
