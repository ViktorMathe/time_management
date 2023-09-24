from django.forms import ModelForm
from .models import Contact, Reply
from manager.models import ManagerProfile  # Import your ManagerProfile model

class Contact_Form(ModelForm):
    class Meta:
        model = Contact
        fields = ['recipient', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super(Contact_Form, self).__init__(*args, **kwargs)

        self.fields['recipient'].widget.attrs['readonly'] = True



class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'subject': 'Subject*',
            'message': 'Message*'
        }

        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False