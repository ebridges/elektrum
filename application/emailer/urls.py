from django.urls import path

from emailer.views.unsubscribe import unsubscribe

urlpatterns = [path('unsubscribe/<uuid:email_id>', unsubscribe, name='unsubscribe')]
