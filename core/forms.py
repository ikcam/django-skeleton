from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Permission, User
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

    def valid_for_company(self, company):
        email = self.cleaned_data.get('email')

        if company.users_all.filter(profile__user__email=email).exists():
            self.add_error(
                'email', _("A user with that email already exists.")
            )

        return not bool(self.errors)


def get_role_form(company):
    permissions_queryset = Permission.objects.all().exclude(
        content_type__app_label__in=(
            'admin', 'authtoken', 'contenttypes', 'sessions'
        )
    ).exclude(
        content_type__app_label='auth', codename='view_user'
    ).exclude(
        content_type__app_label='core', content_type__model='payment'
    ).exclude(
        content_type__app_label='account', content_type__model__in=(
            'colaborator', 'profile'
        )
    ).exclude(
        content_type__app_label='auth', content_type__model__in=(
            'group', 'permission', 'colaborator'
        )
    ).exclude(
        content_type__app_label='core', codename__in=(
            'add_company', 'delete_company', 'add_invoice', 'change_invoice',
            'delete_invoice',
        )
    )

    class RoleForm(forms.ModelForm):
        permissions = forms.ModelMultipleChoiceField(
            label=_("Permissions"), queryset=permissions_queryset,
            required=False, widget=forms.CheckboxSelectMultiple
        )

        class Meta:
            fields = '__all__'
            model = Role

    return RoleForm


class UserChangeForm(UserChangeForm):
    class Meta:
        fields = ('password', 'username', 'first_name', 'last_name', 'email')
        model = User
