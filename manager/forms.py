from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Business, ManagerProfile
from employees.models import EmployeeProfile

class RegisterBusinessForm(forms.ModelForm):
    manager_username = forms.CharField(max_length=30, label='Manager Username')
    manager_email = forms.EmailField(label='Manager Email Address')
    manager_password = forms.CharField(widget=forms.PasswordInput, label='Manager Password')
    manager_password2 = forms.CharField(widget=forms.PasswordInput, label='Manager Password again')
    manager_first_name = forms.CharField(max_length=128, label='Manager First Name')
    manager_last_name = forms.CharField(max_length=128, label='Manager Last Name')

    class Meta:
        model = Business
        fields = ['business_name']
        

    def clean(self):
        try:
            cleaned_data = super().clean()
            manager_username = cleaned_data.get('manager_username')
            try:
                user_with_same_name = User.objects.exclude(pk=self.instance.pk).filter(username=manager_username)
                if user_with_same_name.exists():
                    raise forms.ValidationError(f'Username "{manager_username}" is already in use.')
            except User.DoesNotExist:
                return manager_username
            if 'manager_email' not in cleaned_data:
                raise forms.ValidationError("Manager email field not found in cleaned_data.")
            manager_email = cleaned_data.get('manager_email')
            try:
                user_with_same_email = User.objects.exclude(pk=self.instance.pk).filter(email=manager_email)
                if user_with_same_email.exists():
                    raise forms.ValidationError(f"The following email address already been registered: {manager_email}")
            except User.DoesNotExist:
                return manager_email
            manager_password = cleaned_data.get('manager_password')
            manager_password2 = cleaned_data.get('manager_password2')

            if manager_password and manager_password2 and manager_password != manager_password2:
                self.add_error('manager_password2', "Passwords do not match.")
        except AttributeError as e:
            print("AttributeError in form clean method:", e)
            raise

    def save(self, request=None, commit=True):
        business = super().save(commit=False)
        manager_username = self.cleaned_data['manager_username']
        manager_email = self.cleaned_data['manager_email']
        manager_password = self.cleaned_data['manager_password']
        manager_password2 = self.cleaned_data['manager_password2']
        manager_first_name = self.cleaned_data['manager_first_name']
        manager_last_name = self.cleaned_data['manager_last_name']
        
        # Create the manager's user account
        user = User.objects.create_user(username=manager_username, password=manager_password, email=manager_email)
        user.first_name = manager_first_name
        user.last_name = manager_last_name
        user.is_superuser = True  # Make the manager a superuser
        user.is_staff = False  # Disallow the manager from accessing the admin interface
        group = Group.objects.get(name="managers_admin")
        group.user_set.add(user)
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

    def clean(self):
        try:
            cleaned_data = super().clean()
            username = cleaned_data.get('username')
            try:
                user_with_same_name = User.objects.exclude(pk=self.instance.pk).filter(username=username)
                if user_with_same_name.exists():
                    raise forms.ValidationError(f'Username "{username}" is already in use.')
            except User.DoesNotExist:
                return username
            if 'email' not in cleaned_data:
                raise forms.ValidationError("Email field not found in cleaned_data.")
            email = cleaned_data.get('email')
            try:
                user_with_same_email = User.objects.exclude(pk=self.instance.pk).filter(email=email)
                if user_with_same_email.exists():
                    raise forms.ValidationError(f"The following email address already been registered: {email}")
            except User.DoesNotExist:
                return manager_email
            password1 = cleaned_data.get('password1')
            password2 = cleaned_data.get('password2')

            if password1 and password2 and password1 != password2:
                self.add_error('manager_password2', "Passwords do not match.")
        except AttributeError as e:
            print("AttributeError in form clean method:", e)
            raise

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

    def clean(self):
        try:
            cleaned_data = super().clean()
            username = cleaned_data.get('username')
            try:
                user_with_same_name = User.objects.exclude(pk=self.instance.pk).filter(username=username)
                if user_with_same_name.exists():
                    raise forms.ValidationError(f'Username "{username}" is already in use.')
            except User.DoesNotExist:
                return username
            if 'email' not in cleaned_data:
                raise forms.ValidationError("Email field not found in cleaned_data.")
            email = cleaned_data.get('email')
            try:
                user_with_same_email = User.objects.exclude(pk=self.instance.pk).filter(email=email)
                if user_with_same_email.exists():
                    raise forms.ValidationError(f"The following email address already been registered: {email}")
            except User.DoesNotExist:
                return manager_email
            password1 = cleaned_data.get('password1')
            password2 = cleaned_data.get('password2')

            if password1 and password2 and password1 != password2:
                self.add_error('manager_password2', "Passwords do not match.")
        except AttributeError as e:
            print("AttributeError in form clean method:", e)
            raise

    def save(self, commit=True):
        user = super(EmployeeRegistrationForm, self).save(commit=False)

        if commit:
            user.save()

        return user


class EmployeeApprovalForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ('approved', )

