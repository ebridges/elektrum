"""
elektron URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging

# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']

urlpatterns = [
    path('', include('pages.urls')),
    # path('account/', include('users.urls')),
    # path('account/', include('django.contrib.auth.urls')),
    path('account/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('status/', include('status.urls')),
    path('media/', include('media_items.urls')),
]


class ElektronAccountAdapter(DefaultAccountAdapter, DefaultSocialAccountAdapter):

    def __init__(self, request):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('ElektronAccountAdapter constructed with request.')
    
    def get_connect_redirect_url(self, request, socialaccount):
        self.logger.debug('get_connect_redirect_url() called.')
        return self.redirect_url(request.user.id)

    def get_login_redirect_url(self, request):
        self.logger.debug('get_login_redirect_url() called.')
        return self.redirect_url(request.user.id)

    def redirect_url(self, owner_id):
        self.logger.debug('redirect_url(%s) called.' % owner_id)
        return '/media/{owner_id}/'.format(owner_id=owner_id)
