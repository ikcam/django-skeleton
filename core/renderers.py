from bootstrap4 import renderers


class FieldRenderer(renderers.FieldRenderer):
    def add_class_attrs(self, widget=None):
        super().add_class_attrs(widget=widget)
        if widget is None:
            widget = self.widget

        if self.field.field.disabled:
            widget.attrs['class'] = 'form-control-plaintext'


class FormRenderer(renderers.FormRenderer):
    def render_errors(self, type="non_fields"):
        return super().render_errors(type=type)
