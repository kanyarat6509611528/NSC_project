from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 1:  # Change this to 1 to enforce minimal complexity
            raise forms.ValidationError("This password is too short.")
        return password1