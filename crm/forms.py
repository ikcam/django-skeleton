from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models


def get_customer_model_form(company):
    class ModelForm(forms.ModelForm):
        user = forms.ModelChoiceField(
            label=_("User"),
            queryset=company.users_all.all(),
            required=True,
        )
        source = forms.ModelChoiceField(
            label=_("Source"),
            queryset=company.source_set.all(),
            required=False,
        )

        class Meta:
            fields = '__all__'
            model = models.Customer
            widgets = {
                'address': forms.TextInput,
                'address_2': forms.TextInput,
            }

    return ModelForm


def get_jobdescription_model_form(company):
    class ModelForm(forms.ModelForm):
        parent = forms.ModelChoiceField(
            label=_("Parent"),
            queryset=company.jobdescription_set.all(),
            required=False,
        )

        class Meta:
            fields = '__all__'
            model = models.JobDescription

    return ModelForm


def get_opportunity_model_form(company):
    class ModelForm(forms.ModelForm):
        user = forms.ModelChoiceField(
            label=_("User"),
            queryset=company.users_all.all(),
        )
        person = forms.ModelChoiceField(
            label=_("Person"),
            queryset=company.person_set.all(),
        )
        job_description = forms.ModelChoiceField(
            label=_("Job description"),
            queryset=company.jobdescription_set.all(),
        )

        class Meta:
            fields = '__all__'
            model = models.Opportunity

    return ModelForm


def get_source_model_form(company):
    class ModelForm(forms.ModelForm):
        class Meta:
            fields = '__all__'
            model = models.Source

    return ModelForm


def get_status_model_form(company):
    class ModelForm(forms.ModelForm):
        class Meta:
            fields = '__all__'
            model = models.Status

    return ModelForm
