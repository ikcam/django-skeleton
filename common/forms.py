from django import forms
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from .models import Event, Message

""" Custom field """


class MultipleChoiceField(forms.MultipleChoiceField):
    def clean(self, value):
        super().clean(value)
        return ','.join(value)


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def get_context(self, name, value, attrs):
        value = value.split(',') if value else []
        return super().get_context(name, value, attrs)


def get_event_form(company):
    class EventForm(autocomplete.FutureModelForm):
        model = autocomplete.QuerySetSequenceModelField(
            queryset=autocomplete.QuerySetSequence(
                Message.objects.filter(company=company)
            ),
            required=False,
            widget=autocomplete.QuerySetSequenceSelect2(
                'common:model_autocomplete'
            ),
        )
        notify = MultipleChoiceField(
            label=_("Notify"), choices=Event.NOTIFICATION_OPTIONS,
            widget=CheckboxSelectMultiple,
        )

        class Meta:
            fields = (
                'model', 'share_with', 'date_start', 'date_finish', 'notify',
                'type', 'content'
            )
            model = Event
            widgets = {
                'share_with': autocomplete.ModelSelect2Multiple(
                    url='account:user_other_autocomplete',
                    attrs={'data-placeholder': _("Share with")}
                ),
                'date_start': forms.DateTimeInput(
                    attrs={'type': 'datetime'}
                ),
                'date_finish': forms.DateTimeInput(
                    attrs={'type': 'datetime'}
                ),
            }
    return EventForm
