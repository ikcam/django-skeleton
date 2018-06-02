from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete

from .models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        required=True
    )
    last_name = forms.CharField(
        required=True
    )
    email = forms.EmailField(
        required=True
    )

    class Meta:
        fields = (
            'username', 'password1', 'password2', 'first_name',
            'last_name', 'email'
        )
        model = User

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                _("A user with that email already exists.")
            )

        return data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.is_active = False
            user.save()

        return user


class SignUpInviteForm(UserCreationForm):
    class Meta:
        fields = (
            'username', 'password1', 'password2', 'first_name', 'last_name'
        )
        model = User


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        required=True
    )
    last_name = forms.CharField(
        required=True
    )
    email = forms.EmailField(
        required=True
    )

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                _("A user with that email already exists.")
            )

        return data


class UserUpdateForm(UserChangeForm):
    class Meta:
        fields = (
            'password', 'username', 'first_name', 'last_name', 'email',
            'language', 'timezone', 'photo'
        )
        model = User
        widgets = {
            'language': autocomplete.ListSelect2(
                url='core:language_autocomplete',
            ),
            'timezone': autocomplete.ListSelect2(
                url='core:timezone_autocomplete',
            ),
        }
