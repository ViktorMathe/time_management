from allauth.account.forms import SignupForm


class EmployeeSignupForm(SignupForm):

    def save(self,request):
        user = super(EmployeeSignupForm, self).save(request)

        first_name = forms.CharField(required=True)
        last_name = forms.CharField(required=True)