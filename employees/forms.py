from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from .models import EmployeeProfile, JobRole
from manager.models import Business
import datetime

class DateInput(forms.DateInput):
    input_type = 'date'


class EmployeeSignupForm(SignupForm):

    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    company = forms.ModelChoiceField(queryset=Business.objects.all())
 
    def save(self, request):
        user = super(EmployeeSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        company = self.cleaned_data['company']
        user.save()

        employee_profile = EmployeeProfile.objects.create(
            user=user,
            company=company,
        )

        return user


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ('phone_number', 'birth_date', 'gender', )
        exclude = ('user','line_manager','company','start_date','approved', )

        widgets = { 'birth_date': DateInput()
        }

