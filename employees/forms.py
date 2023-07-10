from allauth.account.forms import SignupForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django import forms
from .models import Timesheet, Business

class RegisterBusinessForm(forms.ModelForm):
    manager_username = forms.CharField(max_length=30, label='Manager Username')
    manager_password = forms.CharField(widget=forms.PasswordInput, label='Manager Password')
    manager_first_name = forms.CharField(max_length=128, label='Manager First Name')
    manager_last_name = forms.CharField(max_length=128, label='Manager Last Name')
    
    class Meta:
        model = Business
        fields = ['business_name', 'business_id']
    
    def save(self, request, commit=True):
        business = super().save(commit=False)
        manager_username = self.cleaned_data['manager_username']
        manager_password = self.cleaned_data['manager_password']
        manager_first_name = self.cleaned_data['manager_first_name']
        manager_last_name = self.cleaned_data['manager_last_name']
        
        # Create the manager's user account
        user = User.objects.create_user(username=manager_username, password=manager_password)
        user.first_name = manager_first_name
        user.last_name = manager_last_name
        user.is_superuser = True  # Make the manager a superuser
        user.is_staff = False  # Allow the manager to access the admin interface
        user.save()
        # Associate the manager's user account with the business
        business.manager = user
        
        if commit:
            business.save()
        
        
        return business



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