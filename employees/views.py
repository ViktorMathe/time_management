from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from .models import Timesheet, AnnualLeave, EmployeeProfile, ManagerProfile
from .forms import ClockingForm, RegisterBusinessForm, EmployeeProfileForm, EmployeeSignupForm, ManagerProfileForm
from allauth.account.forms import LoginForm
from datetime import datetime, date
from django.utils.timezone import utc


def clock_action(request):
    form = ClockingForm()  # Define default form
    error_message = None
    
    if request.method == 'POST':
        # Retrieve form data
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        logging = request.POST.get('logging')
        
        # Authenticate the user
        user = authenticate(request, username=request.user.username, password=password)
        
        if user is not None:
            form = ClockingForm(request.POST)
            
            if form.is_valid():
                timesheet = form.save(commit=False)
                timesheet.employee = user
                timesheet.recorded_by = user
                timesheet.clocking_time = datetime.now()

                if logging == "IN":
                    # Check if the user has already clocked in
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="IN", clocking_time__date=today).first()
                    if existing_timesheet:
                        error_message = f"{user.first_name} {user.last_name} have already clocked in today."
                        logout(request)
                    else:
                        # Perform clock in action
                        timesheet.logging = "IN"
                        timesheet.save()
                        logout(request)
                        return HttpResponse(f"{timesheet.employee} clocked in at {timesheet.clocking_time}")
                elif logging == "OUT":
                    # Check if the user has already clocked out
                    today = date.today()
                    existing_timesheet = Timesheet.objects.filter(employee=user, logging="OUT", clocking_time__date=today).first()
                    if existing_timesheet:
                        error_message = f"{user.first_name} {user.last_name} have already clocked out today."
                        logout(request)
                    else:
                        # Perform clock out action
                        timesheet.logging = "OUT"
                        timesheet.save()
                        logout(request)
                        return HttpResponseRedirect('/timesheet_success/out/?time=%s' % timesheet.clocking_time)
                else:
                    error_message = "Invalid logging value.\n"
            else:
                error_message = "Invalid form data.\n"
        else:
            error_message = "Invalid username or password.\n"
    
    context = {'error_message': error_message, 'form': form}
    return render(request, "index.html", context)


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

    context = {'error_message': error_message, 'login_form':login_form}
    return render(request, "index.html", context)

def timesheet_success(request, in_or_out): # Define function, accept a request and in_or_out
    """ displays to the employee the date and time that they logged in or out """

    timestamp = request.GET.get('time','Error')

    return render("timesheet_success.html", {'in_or_out':in_or_out, 'timestamp':timestamp}, context_instance=RequestContext(request))


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


def business_register(request):
    form = RegisterBusinessForm()
    if request.method == "POST":
        form = RegisterBusinessForm(request.POST)
        if form.is_valid():
           form.save(request)
           logout(request)
           return redirect('home')
        else:
           form = RegisterBusinessForm()

    context = {'form':form}
    return render(request, "reg_business.html", context)


def employee_profile(request):
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
    else:
        form = EmployeeProfileForm(instance=employee)

    template = 'profile.html'
    context= {
        'form': form,
    }
    return render(request, template, context)


def manager_site(request):
    manager = get_object_or_404(ManagerProfile, user=request.user)
    all_employee = EmployeeProfile.objects.all()
    employees = all_employee.filter(company=manager.company)
    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, instance=manager)
        print(form)
        if form.is_valid():
            form.save()
    else:
        form = ManagerProfileForm(instance=manager)
    
    template = 'manager.html'
    context = {
        'form': form,
        'employees': employees,
    }
    return render(request, template, context)