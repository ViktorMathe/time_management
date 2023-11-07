from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Business, ManagerProfile
from employees.models import EmployeeProfile

class RegisterBusinessForm(forms.ModelForm):
    manager_username = forms.CharField(max_length=30, label='Manager Username')
    manager_password = forms.CharField(widget=forms.PasswordInput, label='Manager Password')
    manager_password2 = forms.CharField(widget=forms.PasswordInput, label='Manager Password again')
    manager_first_name = forms.CharField(max_length=128, label='Manager First Name')
    manager_last_name = forms.CharField(max_length=128, label='Manager Last Name')

    class Meta:
        model = Business
        fields = ['business_name']
        

    def clean(self):
        cleaned_data = super().clean()
        manager_password = cleaned_data.get('manager_password')
        manager_password2 = cleaned_data.get('manager_password2')

        if manager_password and manager_password2 and manager_password != manager_password2:
            self.add_error('manager_password2', "Passwords do not match.")

    def save(self, request=None, commit=True):
        business = super().save(commit=False)
        manager_username = self.cleaned_data['manager_username']
        manager_password = self.cleaned_data['manager_password']
        manager_password2 = self.cleaned_data['manager_password2']
        manager_first_name = self.cleaned_data['manager_first_name']
        manager_last_name = self.cleaned_data['manager_last_name']
        
        # Create the manager's user account
        user = User.objects.create_user(username=manager_username, password=manager_password)
        user.first_name = manager_first_name
        user.last_name = manager_last_name
        user.is_superuser = True  # Make the manager a superuser
        user.is_staff = False  # Disallow the manager from accessing the admin interface
        user.save()

        # Associate the manager's user account with the business
        business.manager = user

        if commit:
            business.save()
            # Create the manager profile and associate it with the business
            manager_profile = ManagerProfile.objects.create(user=user, company=business)

        return business


class ManagerInvitationForm(forms.Form):
    email = forms.EmailField(label='Email')


class ManagerRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, label='Username')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Password again')
    first_name = forms.CharField(max_length=128, label='First Name')
    last_name = forms.CharField(max_length=128, label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super(ManagerRegistrationForm, self).save(commit=False)

        # Set additional user attributes
        user.is_superuser = True  # Make the manager a superuser
        user.is_staff = False  # Disallow the manager from accessing the admin interface

        if commit:
            user.save()

        return user


class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = '__all__'
        exclude = ('user','company',)

    def manager_company(self, obj):
        return obj.company


class EmployeeInvitationForm(forms.Form):
    email = forms.EmailField(label='Email')


class EmployeeRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, label='Username')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Password again')
    first_name = forms.CharField(max_length=128, label='First Name')
    last_name = forms.CharField(max_length=128, label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super(EmployeeRegistrationForm, self).save(commit=False)

        if commit:
            user.save()

        return user


class EmployeeApprovalForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ('approved', )

