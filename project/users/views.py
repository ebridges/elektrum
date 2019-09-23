from django.shortcuts import render
from rest_framework.authtoken.models import Token
from base.views.utils import assert_owner_id

def user_profile_view(request, owner_id, template_name='user_profile.html'):
  assert_owner_id(owner_id, request.user.id)
  
  token = Token.objects.filter(user=request.user)

  token_key = None
  if token:
    token_key = token[0].key
  else:
    create_token=bool(request.GET.get('create_token', None))
    if create_token:
      token = Token.objects.create(user=request.user)
      if token:
        token_key = token.key

  return render(request, template_name, { 'token': token_key })
