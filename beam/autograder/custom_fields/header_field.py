from django.forms.fields import Field
from . import widgets


class HeaderField(Field):
    widget = widgets.HeaderWidget

    validators = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clean(self, value=''):
        """
        It seem the clean method in mandatory when creating a Field class.
        Jaust return value without validation
        """
        return value
