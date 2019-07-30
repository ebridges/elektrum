from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('app-home', views.app_home_page_view, name='app-home'),
]
