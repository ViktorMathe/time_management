from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import AnnualLeave, EmployeeProfile
from .forms import EmployeeProfileForm, EmployeeSignupForm
from allauth.account.forms import LoginForm
from datetime import datetime, date
from clocking.views import clock_action


def index(request):
    error_message = ""
    login_form = LoginForm()

    if request.method == "POST":
        # Retrieve form data
        employee_id = request.POST.get('employee_id', '')
        password = request.POST.get('password', '')
        
        # Authenticate the user
        user = authenticate(request, username=employee_id, password=password)
        
        if user is not None:
            login(request, user)  # Log in the authenticated user
            if 'clock_action' in request.POST:
                return clock_action(request)
            elif 'holiday_request' in request.POST:
                return holiday_request(request, user)
            else:
                logout(request)  # Log out the user after form submission
                return redirect('home')  # Redirect to the homepage or any other desired page
        else:
            error_message = "Incorrect Username/Password.\n"

    context = {'error_message': error_message, 'login_form':login_form,}
    return render(request, "index.html", context)


def holiday_request(request, user):
    """ Takes the date and time that the employee requested from / to """ 
    holiday_request = request.POST.get('holiday_request','')
    if holiday_request == "HolidayRequest":
        holiday_req = AnnualLeave(employee=user, recorded_by=user, status=1)
        date_from = request.POST.get('date_from')
        time_from = request.POST.get('time_from')
        date_to = request.POST.get('date_to')
        time_to = request.POST.get('time_to')
        holiday_req.date_from = "%s %s" % (date_from, time_from)
        holiday_req.date_to = "%s %s" % (date_to, time_to)
        holiday_req.save()
        # displays a pending message to the employeee
        return HttpResponseRedirect('/vacation_pending/?datetimefrom=%s&datetimeto=%s' % (holiday_req.date_from, holiday_req.date_to))
    else:
        # error is displayed if conditions are not satisfied
        error_message = "Incorrect Holiday Request.\n"

        context = {'error_message':error_message}
        return render(request, "index.html", context)


def vacation_pending(request):
    """ displays to the employee the dates and times that they requested holidays form / to  """

    date_time_from = request.GET.get('datetimefrom','Error')
    
    date_time_to = request.GET.get('datetimeto','Error')

    return render("vacation_pending.html", {'date_time_from':date_time_from, 'date_time_to':date_time_to,}, context_instance=RequestContext(request))    


@login_required
def holiday_request_action(request, action, holiday_request_id): # Define function, accept a request, action and holiday_request_id
    """ Managemnent login is required. Enables the manager to approve, reject and cancel holiday requests """
    if action == "approve":
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 2
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    elif action == "reject":                    
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 3
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    elif action == "cancel":                    
        annual_leave = AnnualLeave.objects.get(id=holiday_request_id)
        annual_leave.status = 4
        annual_leave.save()
        return HttpResponseRedirect('/loggedin/')
    else:
        # display error massage
        error_message = "Incorrect Holiday Request Action.\n"
        return render("loggedin.html", {'error_message':error_message}, context_instance=RequestContext(request))


@login_required
def employee_profile(request):
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile information has been updated!')
    else:
        form = EmployeeProfileForm(instance=employee)

    template = 'profile.html'
    context= {
        'form': form,
        'employee': employee,
    }
    return render(request, template, context)
