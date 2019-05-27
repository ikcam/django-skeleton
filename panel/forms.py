from django import forms
from django.contrib.auth.forms import (
    PasswordResetForm, UserChangeForm, UserCreationForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from core import models as core
from core.fields import MultipleChoiceField
from core.shortcuts import get_current_company
from core.widgets import CheckboxSelectMultiple


class AccountChangeForm(UserChangeForm):
    username = forms.CharField(disabled=True)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(disabled=True)

    class Meta:
        fields = (
            'password', 'username', 'first_name', 'last_name', 'email',
            'language', 'photo', 'timezone'
        )
        model = core.User


class AccountPasswordResetForm(PasswordResetForm):
    def save(
        self, domain_override=None,
        subject_template_name=(
            'panel/account/account_password_reset_subject.txt'
        ),
        email_template_name='panel/account/account_password_reset_email.html',
        use_https=False, token_generator=default_token_generator,
        from_email=None, request=None, html_email_template_name=None,
        extra_email_context=None
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_company = get_current_company(request)
                company_name = current_company.name
                domain = current_company.domain
            else:
                company_name = domain = domain_override
            context = {
                'email': email,
                'domain': domain,
                'company_name': company_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context,
                from_email, email,
                html_email_template_name=html_email_template_name,
            )


class AccountSignupInviteForm(UserCreationForm):
    email = forms.EmailField(disabled=True)
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password1',
            'password2'
        )
        model = core.User

    def __init__(self, invite, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invite = invite
        self.fields['email'].initial = self.invite.email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.invite.email
        if commit:
            user.save()
            self.invite.user = user
            self.invite.save(update_fields=['user'])
            self.invite.deactivate()
            colaborator, created = user.colaborator_set.get_or_create(
                company=self.invite.company
            )
            for role in self.invite.roles.all():
                colaborator.roles.add(role)
        return user


class CompanyForm(forms.ModelForm):
    domain = forms.CharField(disabled=True)
    email = forms.EmailField(disabled=True)

    class Meta:
        exclude = (
            'is_active', 'user',
            # API Id
            'plivo_id', 'plivo_token', 'signalwire_account',
            'signalwire_token', 'signalwire_space_url',
            'twilio_account', 'twilio_token', 'mailgun_email',
            'mailgun_password', 'modules', 'users'
        )
        model = core.Company
        widgets = {
            'address': forms.TextInput,
            'address_2': forms.TextInput,
        }


def get_colaborator_form(company):
    class ModelForm(forms.ModelForm):
        roles = forms.ModelMultipleChoiceField(
            queryset=company.role_set.all(),
            required=False
        )
        permissions = forms.ModelMultipleChoiceField(
            queryset=company.permission_queryset,
            required=False
        )

        class Media:
            css = {
                'all': (
                    'node_modules/bootstrap-duallistbox/'
                    'dist/bootstrap-duallistbox.min.css',
                ),
            }
            js = (
                'node_modules/bootstrap-duallistbox/'
                'dist/jquery.bootstrap-duallistbox.min.js',
                'panel/js/colaborator_form.js'
            )

        class Meta:
            fields = (
                'is_active', 'roles', 'permissions'
            )
            model = core.Colaborator

    return ModelForm


def get_event_form(company):
    class ModelForm(forms.ModelForm):
        date_start = forms.DateTimeField(
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-toggle': 'datetimepicker',
                    'addon_after': (
                        '<span class="glyphicon glyphicon-calendar"></span>'
                    ),
                }
            )
        )
        date_finish = forms.DateTimeField(
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-toggle': 'datetimepicker',
                    'addon_after': (
                        '<span class="glyphicon glyphicon-calendar"></span>'
                    ),
                }
            )
        )
        notify = MultipleChoiceField(
            choices=core.Event.NOTIFICATION_OPTIONS,
            required=False,
            widget=CheckboxSelectMultiple
        )
        share_with = forms.ModelMultipleChoiceField(
            queryset=company.users.all(),
            required=False
        )

        class Media:
            css = {
                'all': (
                    'node_modules/pc-bootstrap4-datetimepicker/build/css/'
                    'bootstrap-datetimepicker.min.css',
                )
            }
            js = (
                'node_modules/pc-bootstrap4-datetimepicker/build/js/'
                'bootstrap-datetimepicker.min.js',
                'panel/js/event_form.js'
            )

        class Meta:
            exclude = ('model', 'user')
            model = core.Event

        def clean(self):
            cleaned_data = super().clean()
            date_start = cleaned_data.get('date_start')
            date_finish = cleaned_data.get('date_finish')
            notify = cleaned_data.get('notify')

            if all([date_start, date_finish]) and date_start > date_finish:
                self.add_error(
                    'date_finish',
                    _("Finish date must be greater than start date")
                )
            elif date_finish and not date_start:
                self.add_error(
                    'date_start',
                    _("Date start is required when date finish is set.")
                )

            if notify and not date_start:
                self.add_error(
                    'date_start',
                    _("Date start is required when notify is set.")
                )

            return cleaned_data

    return ModelForm


def get_invite_form(company):
    class ModelForm(forms.ModelForm):
        roles = forms.ModelMultipleChoiceField(
            queryset=company.role_set.all(),
            required=False,
        )

        class Meta:
            fields = '__all__'
            model = core.Invite

        def clean_email(self):
            data = self.cleaned_data.get('email')

            qs = company.invite_set.all()

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if (
                qs.filter(email__iexact=data).exists() or
                core.User.objects.filter(email__iexact=data).exists()
            ):
                raise forms.ValidationError(_("Email already exists."))

            return data

    return ModelForm


class LinkForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = core.Link


def get_role_form(company):
    class ModelForm(forms.ModelForm):
        permissions = forms.ModelMultipleChoiceField(
            queryset=company.permission_queryset,
            required=False,
        )

        class Media:
            css = {
                'all': (
                    'node_modules/bootstrap-duallistbox/'
                    'dist/bootstrap-duallistbox.min.css',
                ),
            }
            js = (
                'node_modules/bootstrap-duallistbox/'
                'dist/jquery.bootstrap-duallistbox.min.js',
                'panel/js/role_form.js',
            )

        class Meta:
            fields = '__all__'
            model = core.Role

        def clean_name(self):
            data = self.cleaned_data.get('name')

            qs = company.role_set.all()

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.filter(name__iexact=data).exists():
                raise forms.ValidationError(_("Name already exists."))

            return data

    return ModelForm


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        fields = (
            'username', 'password1', 'password2', 'first_name', 'last_name',
            'email',
        )
        model = core.User

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company

    def clean_email(self):
        data = self.cleaned_data['email']

        if self._meta.model.objects.filter(email=data).exists():
            raise forms.ValidationError(
                _("A user with that email already exists.")
            )

        return data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            user.colaborator_set.get_or_create(company=self.company)

        return user


class UserUpdateForm(UserChangeForm):
    class Meta:
        fields = (
            'password', 'username', 'first_name', 'last_name', 'email',
            'language', 'timezone', 'photo'
        )
        model = core.User
