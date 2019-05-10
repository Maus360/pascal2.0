from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Blog


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username",)


class BlogUpdateForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["name", "description"]
