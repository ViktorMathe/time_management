from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

from .forms import Contact_Form, ReplyForm
from .models import Contact, Reply
from employees.models import EmployeeProfile
from manager.models import ManagerProfile


@login_required
def contact(request):
    recipient_id = request.GET.get('recipient_id')

    if request.method == 'POST':
        form = Contact_Form(request.POST)
        if form.is_valid():
            sender = EmployeeProfile.objects.get(user=request.user)
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            # Check if recipient_id is None or empty before proceeding
            if recipient_id:
                try:
                    recipient = ManagerProfile.objects.get(pk=recipient_id)
                except ManagerProfile.DoesNotExist:
                    # Handle the case where the recipient does not exist
                    recipient = None

                # Create a new message with the sender and recipient if recipient is not None
                if recipient:
                    message = Contact.objects.create(
                        sender=sender,
                        recipient=recipient,
                        subject=subject,
                        message=message_text,
                    )
                    print('success')
                    return redirect('profile')  # Redirect to the message listing page
            else:
                # Handle the case where recipient_id is None (e.g., invalid or not selected)
                # You can add error handling or redirect as needed
                pass
    else:
        # Use recipient_id obtained from the query parameter as initial data
        form = Contact_Form(initial={'recipient': recipient_id})

    # Pass the available managers to the template context
    context = {'form': form}
    return render(request, 'contact.html', context)


@login_required
def contact_messages(request):
    contact_messages = Contact.objects.filter()
    context = {'contact_messages': contact_messages}
    template = 'messages.html'
    return render(request, template, context)


@login_required
def reply(request, contact_us_id):
    user = get_object_or_404(Contact, pk=contact_us_id)
    reply_form = ReplyForm()
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        post_data = request.POST.copy()
        if reply_form.is_valid():
            email = post_data.get('email',)
            subject = post_data.get('subject',)
            body = post_data.get('message',)
            reply_form.save()
            email = email
            subject = subject
            body = body
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(
                request, f'The reply email has been sent to the {user.email}')
            Contact.objects.filter(pk=contact_id).update(answered=True)
            reply_form.save()
            return redirect('messages')
    else:
        reply_form = Contact_Form(initial={'email': user.email,
                                    'subject': f'Re: {user.subject}',
                                             })
    context = {
        'reply_form': reply_form,
        'user': user,
    }
    template = 'reply.html'
    return render(request, template, context)


@login_required
def reply_messages(request):
    reply_messages = Reply.objects.filter()
    context = {'reply_messages': reply_messages}
    template = 'reply_messages.html'
    return render(request, template, context)