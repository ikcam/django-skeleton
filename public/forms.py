from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete

from core.fields import MultipleChoiceField
from core.models import Colaborator, Company, Event, Invite, Link, Role, User
from core.widgets import CheckboxSelectMultiple


def get_colaborator_form(company):
    class ModelForm(forms.ModelForm):
        roles = forms.ModelMultipleChoiceField(
            label=_("Roles"),
            queryset=company.role_set.all(),
            required=False,
        )
        permissions = forms.ModelMultipleChoiceField(
            label=_("Permissions"),
            queryset=company.permission_queryset,
            required=False,
        )

        class Media:
            css = {
                'all': (
                    'bower_components/bootstrap-duallistbox/'
                    'dist/bootstrap-duallistbox.min.css',
                ),
            }
            js = (
                'bower_components/bootstrap-duallistbox/'
                'dist/jquery.bootstrap-duallistbox.min.js',
                'js/colaborator_form.js',
            )

        class Meta:
            fields = ('is_active', 'roles', 'permissions')
            model = Colaborator

    return ModelForm


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        exclude = ('user', 'date_next_invoice', 'custom_domain', )
        model = Company


class CompanyForm(CompanyCreateForm):
    pass


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
                company.message_set.all(),
            ),
            required=False,
            widget=autocomplete.QuerySetSequenceSelect2(
                'public:model_autocomplete',
                attrs={
                    'data-placeholder': _("Object")
                }
            ),
        )
        notify = MultipleChoiceField(
            label=_("Notify"), choices=Event.NOTIFICATION_OPTIONS,
            required=False, widget=CheckboxSelectMultiple
        )
        share_with = forms.ModelMultipleChoiceField(
            label=_("Share with"),
            queryset=User.objects.filter(companies=company),
            required=False,
            widget=autocomplete.ModelSelect2Multiple(
                url='public:user_other_autocomplete',
                attrs={
                    'data-placeholder': _("Share with")
                }
            ),
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
    class ModelForm(forms.ModelForm):
        permissions = forms.ModelMultipleChoiceField(
            label=_("Permissions"),
            queryset=company.permission_queryset,
            required=False,
        )

        class Media:
            css = {
                'all': (
                    'bower_components/bootstrap-duallistbox/'
                    'dist/bootstrap-duallistbox.min.css',
                ),
            }
            js = (
                'bower_components/bootstrap-duallistbox/'
                'dist/jquery.bootstrap-duallistbox.min.js',
                'js/role_form.js',
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

    class Meta:
        fields = (
            'username', 'password1', 'password2', 'first_name', 'last_name',
            'email',
        )
        model = User

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                _("A user with that email already exists.")
            )

        return data


class AccountUpdateForm(UserChangeForm):
    class Meta:
        fields = (
            'password', 'first_name', 'last_name', 'language', 'timezone',
            'photo'
        )
        model = User


class UserUpdateForm(UserChangeForm):
    class Meta:
        fields = (
            'password', 'username', 'first_name', 'last_name', 'email',
            'language', 'timezone', 'photo'
        )
        model = User
