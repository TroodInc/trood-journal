from datetime import datetime

from django.forms import DateTimeField
from django.forms.utils import from_current_timezone


class TimeStampField(DateTimeField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            value = datetime.fromtimestamp(int(value))
            return from_current_timezone(value)
        except:
            result = super(DateTimeField, self).to_python(value)
            return from_current_timezone(result)