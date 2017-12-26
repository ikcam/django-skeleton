from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from .models import Event, Link

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
                    'placeholder': _("Finish date (date)"),
                    'type': 'date-local',
                    'addon_before':
                        '<span class="glyphicon glyphicon-calendar"></span>',
                },
                time_attrs={
                    'placeholder': _("Finish date (time)"),
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
            widget=autocomplete.QuerySetSequenceSelect2(
                'common:model_autocomplete'
            ),
        )
        notify = MultipleChoiceField(
            label=_("Notify"), choices=Event.NOTIFICATION_OPTIONS,
            required=False, widget=CheckboxSelectMultiple
        )
        share_with = forms.ModelMultipleChoiceField(
            label=_("Share with"), queryset=User.objects.all(),
            required=False, widget=autocomplete.ModelSelect2Multiple(
                url='account:user_other_autocomplete',
                attrs={
                    'data-placeholder': _("Share with")
                }
            )
        )

        class Meta:
            fields = (
                'model', 'share_with', 'date_start', 'date_finish', 'notify',
                'type', 'content'
            )
            model = Event

    return EventForm


class LinkForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Link
