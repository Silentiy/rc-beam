from django.forms.widgets import Widget
from django.template.loader import render_to_string


class HeaderWidget(Widget):
    def __init__(self, attrs=None, label=None, tag='h1'):
        self.label = label
        self.tag = tag
        super(HeaderWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        # change blocks/ according to your template path. In this case was templates/block
        widget = render_to_string("autograder/header_form_field.html", {
            "tag": self.tag,
            "label": self.label,
            })
        return widget
