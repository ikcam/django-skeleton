from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from django_addanother.widgets import AddAnotherWidgetWrapper

from core.fields import MultipleChoiceField
from core.models import Colaborator, Company, Event, Invite, Link, Role, User
from core.widgets import CheckboxSelectMultiple


def get_colaborator_form(company):
    class ModelForm(forms.ModelForm):
        roles = forms.ModelMultipleChoiceField(
            label=_("Roles"), queryset=company.role_set.all(),
            required=False, widget=AddAnotherWidgetWrapper(
                forms.SelectMultiple,
                reverse_lazy('public:role_add')
            )
        )

        class Meta:
            fields = ('is_active', 'roles', 'permissions')
            model = Colaborator

    return ModelForm


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        exclude = ('user', 'date_next_invoice', 'custom_domain', )
        model = Company


class CompanyForm(forms.ModelForm):
    class Meta:
        exclude = ('user', 'date_next_invoice', 'custom_domain', )
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


def get_event_form(company):
    class ModelForm(autocomplete.FutureModelForm):
        date_start = forms.SplitDateTimeField(
            label=_("Start date"),
            required=False,
            widget=forms.SplitDateTimeWidget(
                date_attrs={
                    'type': 'date-local',
                    'addon_before':
                        '<span class="glyphicon glyphicon-calendar"></span>',
                },
                time_attrs={
                    'type': 'time-local',
                    'addon_before':
                        '<span class="glyphicon glyphicon-time"></span>',
                }
            )
        )
        date_finish = forms.SplitDateTimeField(
            label=_("Finish date"),
            required=False,
            widget=forms.SplitDateTimeWidget(
                date_attrs={
                    'type': 'date-local',
                    'addon_before':
                        '<span class="glyphicon glyphicon-calendar"></span>',
                },
                time_attrs={
                    'type': 'time-local',
                    'addon_before':
                        '<span class="glyphicon glyphicon-time"></span>',
                }
            )
        )
        model = autocomplete.QuerySetSequenceModelField(
            label=_("Object"),
            queryset=autocomplete.QuerySetSequence(
                company.messages.all(),
            ),
            required=False,
        )
        notify = MultipleChoiceField(
            label=_("Notify"), choices=Event.NOTIFICATION_OPTIONS,
            required=False, widget=CheckboxSelectMultiple
        )
        share_with = forms.ModelMultipleChoiceField(
            label=_("Share with"),
            queryset=User.objects.filter(companies=company),
            required=False,
        )

        class Meta:
            fields = (
                'model', 'share_with', 'date_start', 'date_finish', 'notify',
                'is_public', 'type', 'content'
            )
            model = Event

    return ModelForm


def get_invite_form(company):
    class ModelForm(forms.ModelForm):
        class Meta:
            fields = '__all__'
            model = Invite
            widgets = {
                'roles': autocomplete.ModelSelect2Multiple(
                    url='public:role_autocomplete'
                ),
            }

        def clean_email(self):
            data = self.cleaned_data.get('email')

            qs = company.invite_set.all()

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if (
                qs.filter(email__iexact=data).exists() or
                User.objects.filter(email__iexact=data).exists()
            ):
                raise forms.ValidationError(_("Email already exists."))

            return data

    return ModelForm


class LinkForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Link


def get_role_form(company):
    permissions_queryset = Permission.objects.all().exclude(
        content_type__app_label__in=(
            'admin', 'authtoken', 'contenttypes', 'sessions'
        )
    ).exclude(
        content_type__app_label='core', content_type__model__in=(
            'colaborator', 'notification', 'payment'
        )
    ).exclude(
        content_type__app_label='auth', content_type__model__in=(
            'group', 'permission', 'colaborator'
        )
    ).exclude(
        content_type__app_label='core', codename__in=(
            'add_attachment', 'change_attachment', 'delete_attachment',
            'add_company', 'delete_company',
            'add_invoice', 'change_invoice', 'delete_invoice',
            'add_message', 'change_message', 'delete_message', 'send_message',
            'add_visit', 'change_visit', 'delete_visit',
            'delete_user', 'view_user'
        )
    )

    class ModelForm(forms.ModelForm):
        permissions = forms.ModelMultipleChoiceField(
            label=_("Permissions"), queryset=permissions_queryset,
            required=False, widget=forms.CheckboxSelectMultiple
        )

        class Meta:
            fields = '__all__'
            model = Role

        def clean_name(self):
            data = self.cleaned_data.get('name')

            qs = company.role_set.all()

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.filter(name__iexact=data).exists():
                raise forms.ValidationError(_("Name already exists."))

            return data

    return ModelForm


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


class UserChangeForm(UserChangeForm):
    class Meta:
        fields = ('password', 'username', 'first_name', 'last_name', 'email')
        model = User


class UserUpdateForm(UserChangeForm):
    class Meta:
        fields = (
            'password', 'username', 'first_name', 'last_name', 'email',
            'language', 'timezone', 'photo'
        )
        model = User
