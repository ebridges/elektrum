from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from base.views.utils import assert_owner_id

def user_profile_view(request, owner_id, template_name='user_profile.html'):
  assert_owner_id(owner_id, request.user.id)
  token = Token.objects.filter(user=request.user)
  token_key = None
  if token:
    token_key = token[0].key
  return render(request, template_name, { 'token': token_key })


def user_profile_token_create(request, owner_id):
  assert_owner_id(owner_id, request.user.id)
  token = Token.objects.filter(user=request.user)
  if not token.exists():
    token = Token.objects.create(user=request.user)
  return redirect('user-profile-view', owner_id=owner_id)


def user_profile_token_reset(request, owner_id):
  assert_owner_id(owner_id, request.user.id)
  token = Token.objects.filter(user=request.user)
  if token.exists():
    token_key = token[0].delete()
  return redirect('user-profile-view', owner_id=owner_id)
