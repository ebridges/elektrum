from django.urls import path
from users.views import user_profile_view, user_profile_token_create, user_profile_token_reset

urlpatterns = [
    path('<uuid:owner_id>/', user_profile_view, name='user-profile-view'),
    path(
        '<uuid:owner_id>/create-token', user_profile_token_create, name='user-profile-token-create'
    ),
    path('<uuid:owner_id>/reset-token', user_profile_token_reset, name='user-profile-token-reset'),
]
