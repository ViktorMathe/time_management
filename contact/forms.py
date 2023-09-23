from django.forms import ModelForm
from .models import Contact, Reply


class Contact_Form(ModelForm):
    class Meta:
        model = Contact
        fields = 'phone_number', 'email', 'subject', 'message'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'phone_number': 'Phone Number (Optional)',
            'email': 'Email Address*',
            'subject': 'Subject*',
            'message': 'Message*'
        }

        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False


class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'email': 'Email Address*',
            'subject': 'Subject*',
            'message': 'Message*'
        }

        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False