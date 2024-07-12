from django import forms
from django.contrib.auth.forms import UserCreationForm

from app_users.models import CustomUser
from app_users.models import UserPhobias
from app_general.models import Phobias


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("email",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email"]
        
