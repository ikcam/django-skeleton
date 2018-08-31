from django import forms


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def get_context(self, name, value, attrs):
        if isinstance(value, str):
            value = value.split(',') if value else []
        return super().get_context(name, value, attrs)
