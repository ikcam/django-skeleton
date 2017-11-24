from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from django_addanother.widgets import AddAnotherWidgetWrapper

from account.models import Colaborator
from .models import Company, Invite, Role


def get_colaborator_form(company):
    class ColaboratorForm(forms.ModelForm):
        roles = forms.ModelMultipleChoiceField(
            label=_("Roles"), queryset=Role.objects.filter(company=company),
            required=False, widget=AddAnotherWidgetWrapper(
                autocomplete.ModelSelect2(
                    url='core:role_autocomplete'
                ),
                reverse_lazy('core:role_add')
            )
        )

        class Meta:
            fields = ('is_active', 'roles', 'permissions')
            model = Colaborator
            widgets = {
                'permissions': autocomplete.ModelSelect2Multiple(
                    url='account:permission_autocomplete'
                ),
            }

    return ColaboratorForm


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        exclude = ('user', 'date_next_invoice', 'custom_domain', )
        model = Company
        widgets = {
            'language': autocomplete.ListSelect2(
                url='core:language_autocomplete'
            ),
        }


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
        exclude = ('user', 'date_next_invoice', 'custom_domain', )
        model = Company
        widgets = {
            'language': autocomplete.ListSelect2(
                url='core:language_autocomplete'
            ),
        }


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
