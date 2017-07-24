from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from django_addanother.widgets import AddAnotherWidgetWrapper

from account.models import Colaborator
from .models import Company, Invite, Role


class ColaboratorForm(forms.ModelForm):
    class Meta:
        fields = ('is_active', 'roles', 'permissions')
        model = Colaborator
        widgets = {
            'roles': AddAnotherWidgetWrapper(
                autocomplete.ModelSelect2Multiple(
                    url='core:role_autocomplete'
                ),
                reverse_lazy('core:role_add')
            ),
            'permissions': autocomplete.ModelSelect2Multiple(
                url='account:permission_autocomplete'
            ),
        }


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        exclude = ('user', )
        model = Company


class CulqiTokenForm(forms.Form):
    token = forms.CharField(
        label=_('Token ID'), required=True,
        widget=forms.HiddenInput
    )
    email = forms.EmailField(
        label=_('Email'), required=True,
        widget=forms.HiddenInput
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Company


class InviteForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Invite


class RoleForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Role
        widgets = {
            'permissions': autocomplete.ModelSelect2Multiple(
                url='account:permission_autocomplete',
            )
        }


class UserChangeForm(UserChangeForm):
    class Meta:
        fields = ('password', 'username', 'first_name', 'last_name', 'email')
        model = User
