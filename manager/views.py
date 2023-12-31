from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.tokens import default_token_generator
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import RegisterBusinessForm, ManagerProfileForm, EmployeeApprovalForm, ManagerRegistrationForm, ManagerInvitationForm, EmployeeInvitationForm, EmployeeRegistrationForm
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from invitations.models import Invitation
from invitations.views import AcceptInvite
from .models import ManagerProfile, Business
from employees.models import EmployeeProfile, AnnualLeave
from clocking.models import Timesheet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import datetime
from django import forms


def business_register(request):
    if request.method == "POST":
        business_form = RegisterBusinessForm(request.POST)
        if business_form.is_valid():
           business_form.save(request)
           logout(request)
           return redirect('home')
    else:
         business_form = RegisterBusinessForm()
    context = {'business_form':business_form}
    return render(request, "reg_business.html", context)


@login_required
def send_manager_invitation(request):
    if request.method == "POST":
        invitation_form = ManagerInvitationForm(request.POST)
        if invitation_form.is_valid():
            email = invitation_form.cleaned_data['email']
            try:
                double_invitation = Invitation.objects.filter(email=email)
                if double_invitation.exists():
                    messages.error(request, f'Following email address already been invited: {email}')
                    return redirect('send_manager_invitation')
            except Invitation.DoesNotExist:
                return email

            # Retrieve the user's manager profile and company
            user = request.user
            manager_profile = ManagerProfile.objects.get(user=user)
            company = manager_profile.company
            company_id = company.id

            # Create an invitation using django-invitations
            invitation = Invitation.create(email)
            invitation.sent = timezone.now()  # Set the sent time
            invitation.save()  # Save the invitation to get its key

            # Construct the invitation URL
            invitation_key = invitation.key
            invitation_link = request.build_absolute_uri(reverse('invitations:accept-invite', kwargs={'key': invitation_key}))
            invitation_link += f'?company_id={company_id}&type=manager'

            email_subject = "Invitation to Join as Manager"

            email_message = f"You have been invited to join as a Manager at our company. Please click the following link to register:\n<a href='{invitation_link}'>Accept Invitation</a>"

            send_mail(
                email_subject,
                email_message,
                request.user.email,  # Sender's email
                [email],  # Invited user's email
                fail_silently=False,
            )
            messages.success(request, f"Invitation sent successfully to {email}")
            return redirect('send_manager_invitation')

    else:
        invitation_form = ManagerInvitationForm()

    context = {'invitation_form': invitation_form}
    return render(request, "send_manager_invite.html", context)


class AcceptInviteView(AcceptInvite):
    def post(self, *args, **kwargs):
        invitation = self.get_object()

        if not invitation:
            # Newer behavior: show an error message and redirect.
            messages.error(self.request, 'Invalid invitation. Please try again.')
            return redirect('home')

        if invitation.accepted:
            messages.error(self.request, 'Invitation has already been accepted.')
            return redirect('home')

        if invitation.key_expired():
            messages.error(self.request, 'Invitation has expired.')
            return redirect('home')

        # Store the company_id in the session and redirect to your registration page.
        company_id = self.request.GET.get('company_id')
        registration_type = self.request.GET.get('type')
        self.request.session['company_id'] = company_id
        if registration_type == 'manager':
            # Redirect to manager registration view
            return redirect(reverse('manager_registration', args=[company_id]))
        elif registration_type == 'employee':
            # Redirect to employee registration view
            return redirect(reverse('employee_registration', args=[company_id]))
        else:
            return redirect('home')


def manager_registration(request, company_id):
    if request.method == "POST":
        try:
            business = Business.objects.get(pk=company_id)  # Fetch the Business instance
            form = ManagerRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                manager_profile = ManagerProfile.objects.create(user=user, company=business)
                invitation = get_object_or_404(Invitation, email=manager_profile.user.email)
                try:
                    if not invitation.accepted:
                        # Mark the invitation as accepted
                        invitation.accepted = True
                        invitation.save()
                except Exception as e:
                    message.error(request, f"Error accepting invitation: {e}")

                # Redirect to the manager's dashboard page
                return redirect('account_login')
            else:
                # Get detailed form error messages
                form_errors = form.errors.as_data()
                for field_name, field_errors in form_errors.items():
                    for error in field_errors:
                        messages.error(request, f"{error}")
        except Business.DoesNotExist:
            messages.error(request, "Company not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ManagerRegistrationForm()

    context = {'form': form}
    return render(request, 'manager_register.html', context)


@login_required
def invitations(request):
    accepted_invitations = Invitation.objects.filter(accepted=True)

    pending_invitations = Invitation.objects.filter(accepted=False)

    context= {
         'accepted_invitations': accepted_invitations,
         'pending_invitations': pending_invitations,
    }

    return render(request, 'invitations.html', context)


@login_required
def delete_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    invitation.delete()
    messages.warning(request, f'Invitation for {invitation.email} has been deleted!')
    return redirect(reverse('invitations'))


@login_required
def manager_site(request):
    try:
        manager = get_object_or_404(ManagerProfile, user=request.user)
        all_employee = EmployeeProfile.objects.all()
        all_managers = ManagerProfile.objects.all()
        managers = all_managers.filter(company=manager.company)
        employees = all_employee.filter(company=manager.company)
        manager_form = ManagerProfileForm(instance=manager)
        if request.method == 'POST':
            manager_form = ManagerProfileForm(request.POST, instance=manager)
            if manager_form.is_valid():
                manager_form.save()
                messages.success(
                    request, 'Your profile information has been updated!')
    except Exception as e:
            messages.error(request, "You have not got permission to access the manager page!")
            return redirect('home')
            
    template = 'manager.html'
    context = {
        'manager': manager,
        'manager_form': manager_form,
        'employees': employees,
        'managers': managers,
    }
    return render(request, template, context)


@login_required
def delete_manager(request, id):
    try:
        manager = get_object_or_404(ManagerProfile, id=id)
        user = User.objects.get(username=manager.user)
        user.delete()
        messages.warning(request, f'Manager user: {manager.user.first_name} {manager.user.last_name} has been deleted!')
    except:
        messages.error(request, "User not found!")
    return redirect(reverse('manager'))


@login_required
def send_employee_invitation(request):
    if request.method == "POST":
            employee_invitation_form = EmployeeInvitationForm(request.POST)
            if employee_invitation_form.is_valid():
                email = employee_invitation_form.cleaned_data['email']
                try:
                    double_invitation = Invitation.objects.filter(email=email)
                    if double_invitation.exists():
                        messages.error(request, f'Following email address already been invited: {email}')
                        return redirect('send_employee_invitation')
                except Invitation.DoesNotExist:
                    return email

                # Retrieve the user's manager profile and company
                user = request.user
                manager_profile = ManagerProfile.objects.get(user=user)
                company = manager_profile.company
                company_id = company.id

                # Create an invitation using django-invitations
                invitation = Invitation.create(email)
                invitation.sent = timezone.now()  # Set the sent time
                invitation.save()  # Save the invitation to get its key

                # Construct the invitation URL
                invitation_key = invitation.key
                invitation_link = request.build_absolute_uri(reverse('invitations:accept-invite', kwargs={'key': invitation_key}))
                invitation_link += f'?company_id={company_id}&type=employee'

                email_subject = "Invitation to Join as an Employee"

                email_message = f"You have been invited to join as an Employee at our company. Please click the following link to register:\n<a href='{invitation_link}'>Accept Invitation</a>"

                send_mail(
                    email_subject,
                    email_message,
                    request.user.email,  # Sender's email
                    [email],  # Invited user's email
                    fail_silently=False,
                )
                messages.success(request, f"Invitation sent successfully to {email}")
                return redirect('send_employee_invitation')
    else:
        employee_invitation_form = EmployeeInvitationForm()

    context = {'employee_invitation_form': employee_invitation_form}
    return render(request, "send_employee_invite.html", context)


def employee_registration(request, company_id):
    if request.method == "POST":
        try:
            business = Business.objects.get(pk=company_id)  # Fetch the Business instance

            form = EmployeeRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                employee_profile = EmployeeProfile.objects.create(user=user, company=business)
                invitation = get_object_or_404(Invitation, email=employee_profile.user.email)
                try:
                    if not invitation.accepted:
                        # Mark the invitation as accepted
                        invitation.accepted = True
                        invitation.save()
                except Exception as e:
                    message.error(request, f"Error accepting invitation: {e}")

                # Redirect to the manager's dashboard page
                return redirect('account_login')
            else:
                # Get detailed form error messages
                form_errors = form.errors.as_data()
                for field_name, field_errors in form_errors.items():
                    for error in field_errors:
                        messages.error(request, f"Error in field '{field_name}': {error}")
        except Business.DoesNotExist:
            messages.error(request, "Company not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = EmployeeRegistrationForm()

    context = {'form': form}
    return render(request, 'employee_register.html', context)


@login_required
def approve_employee(request, employee_id):
    employee = get_object_or_404(EmployeeProfile, pk=employee_id)
    if request.method == 'POST':
        approval_form = EmployeeApprovalForm(request.POST, instance=employee)
        if approval_form.is_valid():
            EmployeeProfile.objects.filter(pk=employee_id).update(approved=1)
            approval_form.save()
            return redirect('manager')
    else:
        approval_form = EmployeeApprovalForm(instance=employee)

    
    template = 'approval.html'
    context ={
        'employee': employee,
        'approval_form': approval_form
    }
    return render(request, template, context)


@login_required
def delete_employee(request, id):
    try:
        employee = get_object_or_404(EmployeeProfile, id=id)
        user = User.objects.get(username=employee.user)
        user.delete()
        messages.warning(request, f'Employee user: {employee.user.first_name} {employee.user.last_name} has been deleted!')
    except:
        messages.error(request, "User not found!")
    return redirect(reverse('manager'))


@login_required
def mgnt_clocking(request): #Define function, accept a request 
    """ Managemnent login is required. Enables the manager to clock in/out an employee """
    if request.method == "POST":
        # the employees id, and the managers clock action in/out 
        username = request.POST.get('employee_id', '')        
        mgnt_clock_action = request.POST.get('mgnt_clock_action','')
        # 
        try:
            employee = User.objects.get(username=username)

            if mgnt_clock_action == "ClockIn":
                clockin_date = request.POST.get('clockin_date')
                clockin_time = request.POST.get('clockin_time')
                # create Timesheet with logging = IN, time = now
                timesheet = Timesheet(employee=employee, recorded_by=request.user, logging="IN", ip_address=request.META.get('REMOTE_ADDR','NA'))
                timesheet.clocking_time = "%s %s" % (clockin_date, clockin_time)
                timesheet.save()
                return HttpResponseRedirect('/loggedin/')
            elif mgnt_clock_action == "ClockOut":
                clockin_date = request.POST.get('clockin_date')
                clockin_time = request.POST.get('clockin_time')
                # create Timesheet with logging = IN, time = now
                timesheet = Timesheet(employee=employee, recorded_by=request.user, logging="OUT", ip_address=request.META.get('REMOTE_ADDR','NA'))
                timesheet.clocking_time = "%s %s" % (clockin_date, clockin_time)
                timesheet.save()
                return HttpResponseRedirect('/loggedin/')
            else:
                error_message = "Incorrect Sick Leave Action.\n"
                return render("loggedin.html", {'error_message':error_message}, context_instance=RequestContext(request))
        except Exception as e:
            return render("loggedin.html", {'error_message':"%s"%e}, context_instance=RequestContext(request))
    else:        
        return HttpResponseRedirect('/loggedin/')


@login_required
def loggedin(request):  # Define function, accept a request 
    """ Managemnent login is required. Enables the manager to view and edit employees timesheets and holidays requests"""
    # ORM queries the database for all of the entries.
    timesheets = Timesheet.objects.all() 
    holiday_requests = AnnualLeave.objects.all()

    error_message = ""
    context = {
        'error_message':error_message,
        'full_name':request.user.username,
        'timesheets': timesheets,
        'holiday_requests': holiday_requests,
        'sick_leave': sick_leave,
    }
    
    # Responds with passing the object items (contains info from the DB) to the template loggedin.html 
    return render(request, 'loggedin.html', context)
