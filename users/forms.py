from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import User


class UserRegisterForm(UserCreationForm):

    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Your Username', 'autofocus': 'autofocus'}),
        required=True
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'example@company.com', 'autofocus': 'autofocus'}),
        required=True
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']