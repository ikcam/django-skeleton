from django import forms

from .models import Company, Invite


class CompanyForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Company


class InviteForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Invite
