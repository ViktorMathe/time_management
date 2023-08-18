from django import forms
from .models import Timesheet

class ClockingForm(forms.ModelForm):
    logging = forms.CharField(required=True)

    class Meta:
        model = Timesheet
        fields = ['logging']