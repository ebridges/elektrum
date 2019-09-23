from django.urls import path
from users.views import user_profile_view

urlpatterns = [
    path(r'<uuid:owner_id>/', user_profile_view, name='user-profile-view'),
]
