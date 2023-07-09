from allauth.account.forms import SignupForm
from django import forms
from .models import Timesheet, Business

class RegisterBusinessForm()


class EmployeeSignupForm(SignupForm):

    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    company = forms.ModelChoiceField(queryset=Business.objects.all())
 
    def save(self, request):
        user = super(EmployeeSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class ClockingForm(forms.ModelForm):
    logging = forms.CharField(required=True)

    class Meta:
        model = Timesheet
        fields = ['logging']