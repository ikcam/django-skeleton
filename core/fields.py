from django import forms


class MultipleChoiceField(forms.MultipleChoiceField):
    def clean(self, value):
        super().clean(value)
        return ','.join(value)
