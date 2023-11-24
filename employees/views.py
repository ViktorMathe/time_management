from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AnnualLeave, EmployeeProfile
from .forms import EmployeeProfileForm, EmployeeSignupForm
from clocking.models import Timesheet
from datetime import datetime, date
from itertools import groupby
from operator import attrgetter
from manager.models import ManagerProfile


@login_required
def employee_profile(request):
    try:
        employee = get_object_or_404(EmployeeProfile, user=request.user)
        available_managers = ManagerProfile.objects.filter(company=employee.company)
        if request.method == 'POST':
            form = EmployeeProfileForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Your profile information has been updated!')
    except Exception as e:
            messages.error(request, "Looks like your company has been deleted! Try to contact with your manager.")
            return redirect('home')
        
    template = 'profile.html'
    context= {
        'form': form,
        'employee': employee,
        'available_managers': available_managers
    }
    return render(request, template, context)

@login_required
def view_timesheets(request):
    timesheets = Timesheet.objects.all().filter(employee=request.user)
    grouped_timesheets = {}
    for key, group in groupby(timesheets, key=attrgetter('clocking_time.year', 'clocking_time.month')):
        year, month = key
        grouped_timesheets[f"{year}/{month}"] = list(group)
    template = 'timesheet.html'
    context = {'timesheets': timesheets, 'grouped_timesheets': grouped_timesheets}
    return render(request, template, context)

@login_required
def holidays(request):
    template = 'holidays.html'
    return render(request, template)


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