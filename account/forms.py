from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Profile


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True
    )
    last_name = forms.CharField(
        required=True
    )
    email = forms.EmailField(
        required=True
    )
    password = forms.CharField(
        required=True, widget=forms.PasswordInput, label=_("Password")
    )
    password_confirm = forms.CharField(
        required=True, widget=forms.PasswordInput,
        label=_("Password confirmation")
    )

    class Meta:
        fields = (
            'username', 'password', 'password_confirm', 'first_name',
            'last_name', 'email'
        )
        model = User

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)

        if password != password_confirm:
            self.add_error(
                'password_confirm',
                _("Password confirmation doesn't match the password.")
            )

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                _("A user with that email already exists.")
            )

        return data

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.is_active = False
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        fields = ('username', 'first_name', 'last_name', 'email')
        model = User
