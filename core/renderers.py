from django.forms.widgets import DateInput, DateTimeInput

from bootstrap4 import renderers


class FieldRenderer(renderers.FieldRenderer):
    def add_class_attrs(self, widget=None):
        super().add_class_attrs(widget=widget)
        if widget is None:
            widget = self.widget

        if self.field.field.disabled:
            widget.attrs['class'] = 'form-control-plaintext'

    def add_date_attrs(self, widget=None):
        if not isinstance(widget, DateInput):
            return
        if widget is None:
            widget = self.widget
        widget.attrs["data-datetimepicker"] = widget.attrs.get(
            "data-datetimepicker", "date"
        )

    def add_datetime_attrs(self, widget=None):
        if not isinstance(widget, DateTimeInput):
            return
        if widget is None:
            widget = self.widget
        widget.attrs["data-datetimepicker"] = widget.attrs.get(
            "data-datetimepicker", "datetime"
        )

    def add_widget_attrs(self):
        super().add_widget_attrs()
        if self.is_multi_widget:
            widgets = self.widget.widgets
        else:
            widgets = [self.widget]
        for widget in widgets:
            self.add_date_attrs(widget)
            self.add_datetime_attrs(widget)


class FormRenderer(renderers.FormRenderer):
    def render_errors(self, type="non_fields"):
        return super().render_errors(type=type)
