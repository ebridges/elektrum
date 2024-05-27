from django import forms
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser


class CustomUserCreationForm(SignupForm):
    class Meta(SignupForm):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')
